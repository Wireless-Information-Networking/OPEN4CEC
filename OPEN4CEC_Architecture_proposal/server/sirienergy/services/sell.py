import logging
from services.prices import get_day_ahead_prices

def entsoe_to_array(data):
    max_position = max(int(item['position']) for item in data)
    
    # Initialize the result array with None values
    result = [None] * max_position

    # Fill the result array with prices, filling missing values with the previous one
    previous_value = None
    for item in data:
        position = int(item['position']) - 1  # Convert to 0-based index
        price = float(item['price.amount'])
        
        # Fill any missing positions with the previous value
        if previous_value is not None and position > 0:
            for i in range(position):
                if result[i] is None:
                    result[i] = previous_value
        
        # Set the current price and update the previous value
        result[position] = price
        previous_value = price

    # Fill any remaining None values with the previous value
    for i in range(len(result)):
        if result[i] is None:
            result[i] = previous_value

    return result

def get_price_array(ENTSO_E_API_KEY, country_name, type, fixed_value = 0):
    # validation
    if not isinstance(country_name, str):
        logging.error(f"'country_name' should be a string, got {country_name}")
        return None
    if not isinstance(type, str):
        logging.error(f"'type' should be a string, got {type}")
        return None
    """
    try:
        fixed_value = float(fixed_value)
    except ValueError:
        logging.error(f"'fixed_value' should be a float, got {fixed_value}")
        return None
    """
    # operation
    if type == "FIXED":
        try:
            fixed_value = float(fixed_value)
            size = 24
            price_array = [fixed_value for _ in range(size)]
        except ValueError:
            logging.error(f"'fixed_value' should be a float, got {fixed_value}")
            return None
        
    elif type == "MARKET":
        prices_dict =  get_day_ahead_prices(ENTSO_E_API_KEY, country_name)
        price_array = entsoe_to_array(prices_dict)
        price_array = [round(value/1000, 5) for value in price_array]
    else:
        logging.error("Not valid fee type")
        return None
    return price_array

def sell_by_hours(price_array, gen_array):
    if len(price_array)!= len(gen_array):
        logging.error("Both arrays must have the same length")
        return None 
    return [a*b for a,b in zip(price_array, gen_array)]
