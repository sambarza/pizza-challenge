from cat.looking_glass.cheshire_cat import CheshireCat
from utility import split_long_strings

def is_joke(cat: CheshireCat, content):

   pizze = ""

   for pizza in content["order"]:
         pizze += f"{pizza['quantity']} {pizza['type']}\n"

   PROMPT = f"""
una persona telefona ad una pizzeria e ordina:
{pizze} 
lascia il nome "{content["name"]}"
indirizzo di consegna "{content["address"]}"

rispondi con solo due righe:
sulla prima riga metti solo la percentuale di probabilità che sia uno scherzo telefonico, considerando anche la validità dell'indirizzo di consegna
sulla seconda riga motiva la tua scelta

esempio di risposta:
80%
linguaggio inappropriato
"""

   llm_is_joke_answer = cat.llm(PROMPT)

   return split_long_strings(llm_is_joke_answer.splitlines())