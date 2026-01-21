import os
import random
import google.generativeai as genai
from supabase import create_client

# 1. Configurare Nucleu Axternum
try:
    url = os.environ.get('SUPABASE_URL')
    key = os.environ.get('SUPABASE_KEY')
    genai.configure(api_key=os.environ.get('GEMINI_KEY'))
    supabase = create_client(url, key)
    
    # Modelul ultra-rapid Flash-Lite stabilit anterior
    model = genai.GenerativeModel('models/gemini-2.5-flash-lite-preview-09-2025')
except Exception as e:
    print(f"[-] Eroare critică sistem: {e}")
    exit()

def salveaza_date(username, data):
    """Sincronizează datele locale cu Supabase."""
    supabase.table('players').update(data).eq('username', username).execute()

def joaca():
    print("\n" + "╔" + "═"*43 + "╗")
    print("║    AXTERNUM: EVOLUTION (CORE ENGINE)      ║")
    print("╚" + "═"*43 + "╝")
    
    nume = input("\nIntrodu numele eroului: ").strip()
    res = supabase.table('players').select("*").eq('username', nume).execute()
    
    if not res.data:
        print(f"[*] Profil nou. Se inițializează datele pentru {nume}...")
        initial_stats = {
            "username": nume, 
            "level": 1, 
            "shards": 100, 
            "inventory": [], 
            "hp": 100
        }
        supabase.table('players').insert(initial_stats).execute()
        stats = initial_stats
    else:
        stats = res.data[0]
        # Ne asigurăm că listele nu sunt None
        if stats['inventory'] is None: stats['inventory'] = []

    while True:
        # Mecanică automată de Level Up (la fiecare 250 Shards colectați)
        nivel_nou = (stats['shards'] // 250) + 1
        if nivel_nou > stats['level']:
            stats['level'] = nivel_nou
            salveaza_date(nume, {"level": stats['level']})
            print(f"\n[!!!] EVOLUȚIE: Sistemul tău a urcat la NIVELUL {stats['level']}!")

        print(f"\n[ NIVEL: {stats['level']} | SHARDS: {stats['shards']} | HP: {stats['hp']}/100 ]")
        print("Comenzi: misiune | lupta | magazin | status | iesi")
        comanda = input(f"{nume} > ").lower().strip()

        if comanda == "iesi":
            print("Deconectare... Nucleul Axternum intră în standby.")
            break

        elif comanda == "status":
            print(f"\n--- [ STATUS EROU: {nume.upper()} ] ---")
            print(f"Inventar: {', '.join(stats['inventory']) if stats['inventory'] else 'Gol'}")
            print(f"Shards Totali: {stats['shards']}")
            print("-" * 35)

        elif comanda == "magazin":
            print("\n--- [ MAGAZIN VIRTUAL AXTERNUM ] ---")
            print("1. Sabie de Plasmă (100 Shards) - +25 Atac")
            print("2. Scut de Date (60 Shards) - Reduce damage primit")
            print("3. Refacere HP (30 Shards) - Restaurare 100% HP")
            op = input("Alege o opțiune (1/2/3/anuleaza): ")
            
            if op == "1" and stats['shards'] >= 100:
                stats['shards'] -= 100
                stats['inventory'].append("Sabie de Plasmă")
                salveaza_date(nume, {"shards": stats['shards'], "inventory": stats['inventory']})
                print("[!] Cumpărat: Sabie de Plasmă.")
            elif op == "2" and stats['shards'] >= 60:
                stats['shards'] -= 60
                stats['inventory'].append("Scut de Date")
                salveaza_date(nume, {"shards": stats['shards'], "inventory": stats['inventory']})
                print("[!] Cumpărat: Scut de Date.")
            elif op == "3" and stats['shards'] >= 30:
                stats['shards'] -= 30
                stats['hp'] = 100
                salveaza_date(nume, {"shards": stats['shards'], "hp": 100})
                print("[!] HP restaurat complet!")
            else:
                print("[-] Fonduri insuficiente sau opțiune invalidă.")

        elif comanda == "lupta":
            print("\n[SISTEM]: Se generează un inamic prin Gemini AI...")
            prompt_inamic = "Generează un nume de monstru sci-fi scurt și agresiv."
            nume_inamic = model.generate_content(prompt_inamic).text.strip()
            
            hp_inamic = 30 + (stats['level'] * 20)
            print(f"\nALERTA: {nume_inamic} detectat! (HP Inamic: {hp_inamic})")
            
            while hp_inamic > 0 and stats['hp'] > 0:
                act = input(f"(HP-ul tău: {stats['hp']}) -> [ataca/fugi]: ").lower()
                if act == "ataca":
                    # Calcul damage jucător
                    dmg = random.randint(15, 25)
                    if "Sabie de Plasmă" in stats['inventory']: dmg += 20
                    hp_inamic -= dmg
                    print(f"Lovit! Ai provocat {dmg} damage inamicului.")
                    
                    if hp_inamic > 0:
                        # Calcul damage inamic
                        dmg_in = random.randint(10, 20)
                        if "Scut de Date" in stats['inventory']: dmg_in -= 7
                        stats['hp'] -= max(0, dmg_in)
                        print(f"Inamicul te-a lovit! Ai pierdut {dmg_in} HP.")
                else:
                    print("Ai reușit să fugi, dar ai pierdut ocazia de a câștiga Shards.")
                    break
            
            if hp_inamic <= 0:
                recompensa = random.randint(40, 80) + (stats['level'] * 10)
                stats['shards'] += recompensa
                salveaza_date(nume, {"shards": stats['shards'], "hp": stats['hp']})
                print(f"[VICTORIE]: {nume_inamic} distrus! +{recompensa} Shards.")
            elif stats['hp'] <= 0:
                print("\n[CRITIC]: Ai fost învins. Recuperare de urgență inițiată.")
                stats['hp'] = 20 # Înviere cu 20 HP
                salveaza_date(nume, {"hp": 20})

        elif comanda == "misiune":
            print("\n[NUCLEU]: Se stabilește legătura narativă...")
            prompt = f"Salută-l pe {nume} (Nivel {stats['level']}) și dă-i o misiune scurtă."
            print("\n" + "─"*50)
            print(model.generate_content(prompt).text)
            print("─"*50)

if __name__ == "__main__":
    joaca()