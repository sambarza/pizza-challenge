from cat.mad_hatter.decorators import tool, hook
from cat.looking_glass.cheshire_cat import CheshireCat
import json

from check_joke import is_joke

@hook(priority=0)
def agent_prompt_prefix(prefix, cat):
    """
    This function generates a prefix message that explains the pizza ordering process to the user.
    The prefix message includes the steps involved in the ordering process, the information that will be gathered from the user, and the output schema for the gathered information.
    """
   
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

@hook
def agent_prompt_suffix(suffix, cat):
   """
   Inserendo il primo turn "Buongiorno" fisso, l'LLM riesce meglio a capire che la prima
   domanda contiene già informazioni utili per l'ordine
   """

   suffix = """
# Context

{episodic_memory}

{declarative_memory}

{tools_output}

## Conversation until now:
 - Human: Buongiorno
 - AI: Buongiorno! Come posso aiutarti? Vorresti ordinare una pizza?
{chat_history}
 - Human: {input}
 - AI: """

   return suffix

@hook()
def agent_after_execution_memory_chain(message, cat):
   """
   This function is called before the Cheshire Cat sends a message. It checks if the message content is a JSON object,
   and if so, checks if it indicates the end of a flow process. If the flow process is an order confirmation, the function
   places the order.
   """
      
   try:
      # Is it a JSON message?
      content = json.loads(message["output"])
   except:
      # Not a JSON message, return as is (I hope is not a malformed order confirmation!)
      return message
   
   # Is the end of a flow process?
   if "flow" in content:

      # Order confirmation?
      if content["flow"] == "order_confirmed":
         
         # Order validation       
         order_validation_result = order_validation(content, message, cat)
         if order_validation_result:
            return order_validation_result

         # Place the order
         order_placing_result = place_order(content, message, cat)
         if order_placing_result:
            return order_placing_result

@hook()
def before_cat_sends_message(message, cat):

   # Order placed?
   if message["content"] == "Thank you, order confirmed.":

      # After order placement
      after_order_placement(cat)

def order_validation(order, message, cat: CheshireCat):

   # Cannot order pizza for myself!
   if order["name"].lower() == "stregatto":
      message["output"] = "I'm sorry! I can't place an order for myself! Please give a new name"
      return message
   
   # For each pizza type in the order      
   for pizza in order["order"]:
      # Hawaian pizza is banned!
      if pizza['type'].lower() == "hawaian":
         message["output"] = "I'm sorry! Hawaian pizza is banned! Which pizza do you want instead of it?"
         return message

def place_order(order, message, cat: CheshireCat):
   """
   Places an order for pizza and sends a confirmation message to the user.
   """
   # Place the order 

   try:

      # Check if the order is a joke
      scherzo, *reason = is_joke(cat, order)

      # Print the order confirmation header
      print(f"§ ╔════════════════════════════════════════════════════════════════════════════════╗")
      print(f"§ ║                      PIZZA CHALLENGE  ORDER CONFIRMED                          ║")
      print(f"§ ╠════════════════════════════════════════════════════════════════════════════════╣")
      print(f'§ ║ SCHERZO: {scherzo.ljust(70)}║')
      print(f'§ ║ MOTIVO:                                                                        ║')
      for line in [line for line in reason if line.strip()]:
         if line:
            print(f'§ ║ {line.ljust(79)}║')
      print(f"§ ╠════════════════════════════════════════════════════════════════════════════════╣")
      print(f'§ ║ {order["name"].ljust(79)}║')
      print(f'§ ║ {order["address"].ljust(79)}║')

      # For each pizza type in the order      
      for pizza in order["order"]:

         # Prepare the pizza info string
         pizza_info=f"{pizza['quantity']} x {pizza['type']}"

         # Print the pizza type and quantity
         print(f'§ ║ {pizza_info.ljust(79)}║')

         # Print additional info for each pizza type
         for key in pizza.keys():
            if key != "quantity" and key != "type":
               note=f"     {key}: {pizza[key]}"
               print(f"§ ║ {note.ljust(79)}║")

      print(f"§ ╚════════════════════════════════════════════════════════════════════════════════╝")

      # Send the order confirmation message
      message["output"] = "Thank you, order confirmed."

   except Exception as e:
      print(e)
      message["output"] = "I'm sorry! There was a problem placing your order."

   # Return the message
   return message

def after_order_placement(cat: CheshireCat):

   try:

      # Clear the working memory and history
      new_order(cat)

   except Exception as e:
      print("Exception after order placing, order probably already placed")
      print(e)

def new_order(cat: CheshireCat):
   """
   Each order flow is completely independent from the previous one.
   This function clears the working memory and the history of the Cheshire Cat.
   """
   cat.working_memory.episodic_memory.clear()
   cat.working_memory.history.clear()