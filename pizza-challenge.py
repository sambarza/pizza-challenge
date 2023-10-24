from cat.mad_hatter.decorators import tool, hook
from cat.looking_glass.cheshire_cat import CheshireCat
import json

@hook()
def before_cat_sends_message(message, cat):
   try:
      content = json.loads(message["content"])
      if content["flow"] == "order_confirmed":

         scherzo, reason = is_scherzo(cat, content)

         print(f"╔═════════════════════════════════════════╗")
         print(f"║     PIZZA CHALLENGE  ORDER CONFIRMED    ║")
         print(f"╠═════════════════════════════════════════╣")

         print(f'║ SCHERZO: {scherzo.ljust(31)}║')
         print(f'║ MOTIVO: {reason.ljust(32)}║')

         print(f"╠═════════════════════════════════════════╣")
         print(f'║ {content["name"].ljust(40)}║')
         print(f'║ {content["address"].ljust(40)}║')
         for pizza in content["order"]:
            pizza_info=f"{pizza['quantity']} x {pizza['type']}"
            print(f'║ {pizza_info.ljust(40)}║')
            for key in pizza.keys():
               if key != "quantity" and key != "type":
                  note=f"     {key}: {pizza[key]}"
                  print(f"║ {note.ljust(40)}║")
         print(f"╚═════════════════════════════════════════╝")

         new_order(cat)

   except:
      pass

   return message

def new_order(cat: CheshireCat):
   cat.working_memory.episodic_memory.clear()
   cat.working_memory.history.clear()
   
def is_scherzo(cat: CheshireCat, content):

   pizze = ""

   for pizza in content["order"]:
         pizze += f"{pizza['quantity']} {pizza['type']}\n"

   PROMPT = f"""
una persona telefona ad una pizzeria e ordina:
{pizze} 
a nome {content["name"]} 
consegna in {content["address"]}
ti sembra uno scherzo?

rispondi sulla prima riga solo con: SI/NO/PROBABILE
sulla seconda riga con la motivazione della tua scelta
"""

   print(PROMPT)
   risposta = cat.llm(PROMPT)
   print(f"Risposta: {risposta}")

   return risposta.split("\n")
            
@hook(priority=0)
def agent_prompt_prefix(prefix, cat):
   prefix = """
Here's how the pizza ordering process exactly works:
   1. Initiating an Order:
      - When someone asks to order a pizza, I will start by asking for the necessary information, one by one.
   2. Gathering Information:
      - I will ask for the following information.
      - Type of pizza.
      - Name for the order.
      - Delivery address.
   3. Validating Information:
      - I will validate the provided information.
      - Check the quantity.
      - Verify that the delivery address is a valid Italian address.
   4. Order Confirmation:
      - I will ask for confirmation from the user before placing the order.
   5. Placing the Order:
      - When the user confirms the order, I will always provide the gathered information always and only in JSON format that conforms to the JSON schema below.

        Here is the output schema:
        ```
        {{"properties": {{"name": {{"title": "Name", "description": "name of the order", "type": "string"}}, "address": {{"title": "Address", "description": "address of the order", "type": "string"}}, "order": {{"title": "Order", "description": "list of pizza ordered", "type": "array", "items": {{"$ref": "#/definitions/OrderPizza"}}}}}}, "required": ["name", "address", "order"], "definitions": {{"OrderPizza": {{"title": "OrderPizza", "type": "object", "properties": {{"type": {{"title": "Type", "description": "type of pizza", "type": "string"}}, "quantity": {{"title": "Quantity", "description": "quantity of pizza", "type": "integer"}}}}, "required": ["type", "quantity"]}}}}}}
   6. Process Completion:
      - I will reply with a message indicating that the order is complete.
      - I will then end the chat.

This is an example of a valid conversation:
   Human: Hi,
   Bot: Hi, I am a pizza ordering assistant. How can I help you?
   Human: I want two margherita
   Bot: Ok two margherita, What is the name for the order?
   Human: And one napoli
   Bot: Ok two margherita and one napoli, What is the name for the order?
   Human: John
   Bot: What is the delivery address?
   Human: cornizzolo 55 eupilio
   Bot: Ok, I have the following order: two margherita and one napoli for John, to be delivered at cornizzolo 55 eupilio. Is this correct?
   Human: yes
   Bot: {{"flow":"order_confirmed", "name": "John", "address": "cornizzolo 55 eupilio", "order": [{{"type": "margherita", "quantity": 2 }}, {{"type": "napoli", "quantity": 1}}]}}  

Now you are a pizza's assistance that respect exactly the ordering process.
You will start the chat by asking me to order a pizza.
   """

   return prefix