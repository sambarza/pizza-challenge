from cat.mad_hatter.decorators import tool, hook
from cat.looking_glass.cheshire_cat import CheshireCat
import json

@hook()
def before_cat_sends_message(message, cat):
      
   try:
      # Is it a JSON message?
      content = json.loads(message["content"])
   except:
      # Not a JSON message, return as is (I hope is not a malformed order confirmation!)
      return message
   
   # Is the end of a flow process?
   if "flow" in content:

      # Order confirmation?
      if content["flow"] == "order_confirmed":

         # Yes! Place the order
         return place_order(content, message, cat)

def place_order(order, message, cat: CheshireCat):
   # Place the order 

   # --------------------------------------
   # JSON order example:
   # --------------------------------------
   # {
   #  "flow": "order_confirmed",
   #  "name": "John",
   #  "address": "cornizzolo 55 eupilio",
   #  "order": [
   #      {
   #          "type": "margherita",
   #          "quantity": 2
   #          "notes": "senza mozzarella" # sometimes the LLM add additional info in casual other keys...
   #      },
   #      {
   #          "type": "napoli",
   #          "quantity": 1
   #      }
   #  ]
   # }
   try:

      # Check if the order is a joke
      scherzo, *reason = is_joke(cat, order)
      
      # Print the order confirmation header
      print(f"╔═════════════════════════════════════════╗")
      print(f"║     PIZZA CHALLENGE  ORDER CONFIRMED    ║")
      print(f"╠═════════════════════════════════════════╣")
      print(f'║ SCHERZO: {scherzo.ljust(31)}║')
      print(f'║ MOTIVO:                                 ║')
      for line in [line for line in reason if line.strip()]:
         if line:
            print(f'║ {line.ljust(40)}║')
      print(f"╠═════════════════════════════════════════╣")
      print(f'║ {order["name"].ljust(40)}║')
      print(f'║ {order["address"].ljust(40)}║')

      # For each pizza type in the order      
      for pizza in order["order"]:

         # Prepare the pizza info string
         pizza_info=f"{pizza['quantity']} x {pizza['type']}"

         # Print the pizza type and quantity
         print(f'║ {pizza_info.ljust(40)}║')

         # Print additional info for each pizza type
         for key in pizza.keys():
            if key != "quantity" and key != "type":
               note=f"     {key}: {pizza[key]}"
               print(f"║ {note.ljust(40)}║")

      print(f"╚═════════════════════════════════════════╝")

      # Clear the working memory and history
      new_order(cat)

      # Send the order confirmation message
      message["content"] = "Thank you, order confirmed."

   except Exception as e:
      print(e)
      message["content"] = "I'm sorry! There was a problem placing your order."

   # Return the message
   return message

def new_order(cat: CheshireCat):
   cat.working_memory.episodic_memory.clear()
   cat.working_memory.history.clear()
   
def is_joke(cat: CheshireCat, content):

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
   llm_is_joke_answer = cat.llm(PROMPT)
   print(f"Risposta: {llm_is_joke_answer}")

   return llm_is_joke_answer.splitlines()
            
@hook(priority=0)
def agent_prompt_prefix(prefix, cat):
   prefix = """
Here's how the pizza ordering process exactly works:
   1. Initiating an Order:
      - When someone asks to order a pizza, I will start by asking for the necessary information, one by one.
      - I will take into consideration all the information contained in the initial question.
   2. Gathering Information:
      - I will ask for the following information.
      - Type of pizza.
      - Name for the order.
      - Delivery address.
   3. Order Confirmation:
      - I will ask for confirmation from the user before placing the order.
   4. Placing the Order:
      - Before this step the order can still be canceled.
      - When the user confirms the order, I will always provide the gathered information always and only in JSON format that conforms to the JSON schema below.

        Here is the output schema:
        ```
        {{"properties": {{"name": {{"title": "Name", "description": "name of the order", "type": "string"}}, "address": {{"title": "Address", "description": "address of the order", "type": "string"}}, "order": {{"title": "Order", "description": "list of pizza ordered", "type": "array", "items": {{"$ref": "#/definitions/OrderPizza"}}}}}}, "required": ["name", "address", "order"], "definitions": {{"OrderPizza": {{"title": "OrderPizza", "type": "object", "properties": {{"type": {{"title": "Type", "description": "type of pizza", "type": "string"}}, "quantity": {{"title": "Quantity", "description": "quantity of pizza", "type": "integer"}}}}, "required": ["type", "quantity"]}}}}}}

This is an example of a valid conversation:
   Human: Hi,
   Bot: Hi, I am a pizza ordering assistant. How can I help you?
   Human: I want two margherita
   Bot: Ok two margherita, What name should I put for the delivery?
   Human: And one napoli
   Bot: Ok two margherita and one napoli, What name should I put for the delivery?
   Human: Joe & Mac
   Bot: What is the delivery address?
   Human: cornizzolo 55 eupilio
   Bot: Ok, I have the following order: two margherita and one napoli, name for the delivery is "Joe & Mac", to be delivered at cornizzolo 55 eupilio. Is this correct?
   Human: yes
   Bot: {{"flow":"order_confirmed", "name": "John", "address": "cornizzolo 55 eupilio", "order": [{{"type": "margherita", "quantity": 2 }}, {{"type": "napoli", "quantity": 1}}]}}  

Now you are a pizza's assistance that respect exactly the ordering process.
You will start the chat by asking me to order a pizza.
   """

   return prefix