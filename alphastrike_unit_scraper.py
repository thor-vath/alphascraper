import json
from pathlib import Path
from urllib.parse import unquote
import requests
requests.packages.urllib3.disable_warnings()

FACTION_IDS = {
    "draconis_combine":"27",
    "wolfs_dragoons":"49"
        }

ERA_IDS = {
    "clan_invasion":"13"
        }
        
def remove_url_formatting(str_to_clean):
    """ Clean out URL formatting from a string """
    clean_str = str_to_clean.replace('&quot;','"')
    clean_str = clean_str.replace('&#39;', "'")
    clean_str = clean_str.replace('&#243;', 'o')
    return clean_str

def save_unit_links(faction_id=49, era_id=13, outfile="unitlinks.txt"):
    """ Make a reques to get the links to a faction and eras units and save it """

    url_host = "www.masterunitlist.info"
    url_path = f"/Era/FactionEraDetails?FactionId={faction_id}&EraId={era_id}"
    r = requests.get(f"https://{url_host}{url_path}", verify=False)

    if r.status_code != 200:
        raise ValueError(f"get_unit_links expected 200, got {r.status_code}")

    with open(outfile, 'w') as f:
        f.writelines(r.text)

    return outfile



def get_unit_links(faction_id=49, era_id=13, linkfile=None):
    """ Get a list of units related to a faction and era """

    if linkfile is None:
        linkfile = save_unit_links(faction_id, era_id)
    
    link_dict = {}

    # OLD CODE - parsing the 
    # ~ # Find where the unit string starts
    # ~ unit_detail_start = r.text.find("/Unit/Details")
    # ~ print(unit_detail_start)
    
    # ~ # Find the instance of /Unit/Details then look forward from there
    # ~ # The unit id will be between /, and then the unit name will end with a "

    # ~ # find where the unit string ends
    # ~ unit_detail_end = r.text[unit_detail_start:].find('"')
    # ~ print(unit_detail_end)

    # ~ # Get the string like /123/firmoth-a
    # ~ unit_str = r.text[unit_detail_start:unit_detail_start+unit_detail_end]
    # ~ # Split the unit string apart to get the numbers into the dictionary
    # ~ # ['', 'Unit', 'Details', '838', 'dasher-fire-moth-a']
    # ~ unit_id = unit_str.split('/')[3]
    # ~ unit_linkname = unit_str.split('/')[4]

    # ~ link_dict[str(unit_id)] = unit_linkname
    
    # ~ print(link_dict)

    with open(linkfile, 'r') as f:
        line = f.readline()
        while line:
            unit_detail_start = line.find("/Unit/Details")
            if unit_detail_start >= 0:
                # ~ print(unit_detail_start) # testing
                # We found a unit link
                unit_detail_end = line[unit_detail_start:].find('"')
                # ~ print(unit_detail_end) # testing
                unit_str = line[unit_detail_start:unit_detail_start+unit_detail_end]
                unit_id = unit_str.split('/')[3]
                # ~ print(unit_id) # testing
                unit_linkname = unit_str.split('/')[4]
                # ~ print(unit_linkname) # testing
                link_dict[str(unit_id)] = unit_linkname
            line = f.readline()

    # link_dict is a dictionary, keys are the unit_id, and the value is the unit_linkname
    
    return link_dict
                

def request_unit_info(unit_id, unit_linkname):
    """ Get a collection of unit info, given its ID and name """

    unit_data = {
        "unit_id":unit_id,
        "unit_linkname":unit_linkname,
        "tonnage":"none",
        "bv":"none",
        "cost":"none",
        "rules_level":"none",
        "tech":"none",
        "type":"none",
        "role":"none",
        "intro_date":"none",
        "era":"none",
        "name":"none",
        "model":"none",
        "pv":"none",
        "tp":"none",
        "size":"none",
        "move":"none",
        "jump_capable":"none",
        "dmg_s":"none",
        "dmg_m":"none",
        "dmg_l":"none",
        "dmg_e":"none",
        "ov":"none",
        "armor":"none",
        "struc":"none",
        "threshold":"none",
        "specials":"none",
        "img_url":"none"
        }
        

    url_1_host = "www.masterunitlist.info"
    url_2_host = url_1_host
    
    url_1_path = f"/Unit/Details/{str(unit_id)}/{unit_linkname}"
    url_2_path = f"/Tools/CustomCard/{unit_id}"


    def extract_value_from_page_one(text, proper_value_name, value_start_str="<dd>", value_end_str="</dd>"):
        """ Take a proper value name like 'Battle Value' and get the numeric quantity from page 1 """
        value_text_start = text.find(proper_value_name)
        # TODO error checking here
        value_start = value_text_start + text[value_text_start:].find(value_start_str) + len(value_start_str)
        value_end = value_start + text[value_start:].find(value_end_str)
        value = text[value_start:value_end].strip()
        value = remove_url_formatting(value)
        return value

    def extract_value_from_page_two(text, proper_value_name, value_start_str='value="', value_end_str='"'):
        """ Extract a piece of mech info from the customize page """
        input_ph_start = text.find(f'placeholder="{proper_value_name}"')
        value_start = input_ph_start + text[input_ph_start:].find(value_start_str) + len(value_start_str)
        value_end = value_start + text[value_start:].find(value_end_str)
        value = text[value_start:value_end].strip()
        value = remove_url_formatting(value)
        return value

    r = requests.get(f"https://{url_1_host}{url_1_path}", verify=False)
    if r.status_code != 200:
        raise ValueError(f"get_unit_info expected status 200, got {r.status_code}")

    # TONNAGE
    unit_data["tonnage"] = extract_value_from_page_one(r.text, "Tonnage")
    
    # BATTLE VALUE
    unit_data["bv"] = extract_value_from_page_one(r.text, "Battle Value")

    # COST
    unit_data["cost"] = extract_value_from_page_one(r.text, "Cost")
    
    # RULES LEVEL - rules_level
    unit_data["rules_level"] = extract_value_from_page_one(r.text, "Rules Level")

    # TECH - tech
    unit_data["tech"] = extract_value_from_page_one(r.text, "Technology")
    
    # TYPE - type
    unit_data["type"] = extract_value_from_page_one(r.text, "Unit Type")
    
    # ROLE - role
    unit_data["role"] = extract_value_from_page_one(r.text, "Unit Role")
    
    # INTRO DATE - intro_date
    unit_data["intro_date"] = extract_value_from_page_one(r.text, "Date Introduced")
    
    # ERA - era
    unit_data["era"] = extract_value_from_page_one(r.text, "Era</dt>")

    if r.text.find('src="/Unit/Card/') < 0:
        # Could not find card data
        print("Err: cannot find card data")
        return unit_data

    # PAGE 2
    r = requests.get(f"https://{url_2_host}{url_2_path}", verify=False)
    if r.status_code != 200:
        raise ValueError(f"get_unit_info expected status 200, got {r.status_code}")

    unit_data["name"] = extract_value_from_page_two(r.text, "Name")

    unit_data["model"] = extract_value_from_page_two(r.text, "Model")

    unit_data["pv"] = extract_value_from_page_two(r.text, "Point Value")

    unit_data["tp"] = extract_value_from_page_two(r.text, "Type")

    unit_data["size"] = extract_value_from_page_two(r.text, "Size")

    unit_data["move"] = extract_value_from_page_two(r.text, "Move")
    if '&quot;' in unit_data["move"]:
        unit_data["move"] = unit_data["move"].replace('&quot;','')

    if 'j' in unit_data["move"]:
        unit_data["jump_capable"] = "True"
    else:
        unit_data["jump_capable"] = "False"


    unit_data["dmg_s"] = extract_value_from_page_two(r.text, "Short")

    unit_data["dmg_m"] = extract_value_from_page_two(r.text, "Medium")

    unit_data["dmg_l"] = extract_value_from_page_two(r.text, "Long")

    unit_data["dmg_e"] = extract_value_from_page_two(r.text, "Extreme")

    unit_data["ov"] = extract_value_from_page_two(r.text, "Overheat")

    unit_data["armor"] = extract_value_from_page_two(r.text, "Armor")

    unit_data["struc"] = extract_value_from_page_two(r.text, "Structure")

    unit_data["threshold"] = extract_value_from_page_two(r.text, "Threshold")

    unit_data["specials"] = extract_value_from_page_two(r.text, "Specials", 'rows="2">', '</textarea>').strip()

    unit_data["img_url"] = extract_value_from_page_two(r.text, "Image", 'rows="2">', '</textarea>').strip()
    
    return unit_data

def write_unit_data(unit_data, overwrite=False, data_dir="alphastrike_unit_data"):

    unit_data_json = json.dumps(unit_data)
    unit_id = unit_data["unit_id"]
    unit_linkname = unit_data["unit_linkname"]
    
    # If we are not overwriting, then exit
    if not overwrite:
        if Path(f"{data_dir}/{unit_id}/{unit_linkname}.json").is_file():
            return False

    # Create the path
    Path(f"{data_dir}/{unit_id}").mkdir(parents=True, exist_ok=True)

    # Write data to file
    with open(f"{data_dir}/{unit_id}/{unit_linkname}.json", 'w') as f:
        f.write(unit_data_json)
        
    return True

def get_unit_from_disk(unit_id, unit_link, data_dir="alphastrike_unit_data"):
    """ Load a unit from a local JSON file """
    # This format is set in the write function
    unit_file_path = f"{data_dir}/{unit_id}/{unit_link}.json"
    if Path(unit_file_path).is_file():
        with open(unit_file_path, 'r') as f:
            return json.load(f)
    else:
        # TODO raise an error instead or just return False?
        return False
    
def get_single_unit_data(unit_id, unit_link, force_download=False, overwrite=True, data_dir="alphastrike_unit_data"):
    """ Get a single unit's data, check local cache as well """

    # check if the unit data is cached on the local filesystem first
    unit_cache_file = f"{data_dir}/{unit_id}/{unit_link}.json"
    if Path(unit_cache_file).is_file() and not force:
        # We have cached unit data
        with open(unit_cache_file, 'r') as unit_cache_file:
            unit_data = json.load(unit_cache_file)
    else:
        unit_data = request_unit_info(unit_id, unit_link)
        
    # We shouldn't write in this function, it isn't expected
    #write_unit_data(unit_data, unit_id, unit_link, overwrite=force)
    
    return unit_data

def convert_unit_data_to_csv(unit_data, headers=False, delim=';'):
    """ Convert a unit_data dict to a CSV string """
    csv_str = ""
    if headers:
        for header in unit_data.keys():
            if csv_str == "":
                csv_str = header
            else:
                csv_str = f"{csv_str}{delim}{header}"
    else:
        for header in unit_data.keys():
            if csv_str == "":
                csv_str = unit_data[header]
            else:
                csv_str = f"{csv_str}{delim}{unit_data[header]}"
                
    return csv_str

def request_era_id_mapping(faction_id):
    """ Make a request to a faction's page and find all their available eras """
    era_dict = {}
    era_url = f"https://masterunitlist.info/Faction/Details/{faction_id}"
    
    r = requests.get(era_url, verify=False)

    id_search = f'EraId='
    name_search = 'title="'
    id_start = r.text.find(id_search)
    last_index = 0
    while id_start >= 0:
        id_start = id_start + last_index + len(id_search)
        id_end = r.text[id_start:].find('"')
        id_end = id_end + id_start
        era_id = r.text[id_start:id_end]

        name_start = r.text[id_end:].find(name_search)
        name_start = name_start + id_end + len(name_search)
        name_end = r.text[name_start:].find('"')
        name_end = name_end + name_start
        era_name = r.text[name_start:name_end]
        era_name = remove_url_formatting(era_name)

        era_dict[era_id] = era_name

        last_index = name_end
        id_start = r.text[last_index:].find(id_search)

    return era_dict
    
    
    

def request_faction_id_mapping():
    """ Make a reques to the faction list and get a mapping of faction ID to faction name """
    # Should return a dictionary with faction ID as key and name as value
    faction_index_url = "https://www.masterunitlist.info/Faction/Index"
    r = requests.get(faction_index_url, verify=False)
    if r.status_code != 200:
        raise ValueError(f"Expected status code 200 but received {r.status_code} when requesting {faction_index_url}")
        
    faction_dict = {} # faction_dict[key==id] value==name

    # Define the substrings to locate the ID and name
    id_search_text = "/Faction/Details/"
    faction_name_search_text = '<strong style="vertical-align:bottom;">'

    # Prime the loop to find all the Faction IDs and Faction names then add them to faction_dict
    id_search_result = r.text.find(id_search_text)
    last_index = 0
    while id_search_result >= 0:
        # Find Faction ID
        id_start = last_index + id_search_result + len(id_search_text)
        id_end = r.text[id_start:].find('"') + id_start
        faction_id = r.text[id_start:id_end] # the faction ID
        
        last_index = id_end
        
        # Find Faction Name
        faction_name_start = r.text[last_index:].find(faction_name_search_text) + last_index + len(faction_name_search_text)
        faction_name_end = r.text[faction_name_start:].find('<') + faction_name_start
        faction_name = r.text[faction_name_start:faction_name_end].strip()
        faction_name = remove_url_formatting(faction_name)

        last_index = faction_name_end

        # Add ID and Name to dict
        faction_dict[str(faction_id)] = faction_name

        id_search_result = r.text[last_index:].find(id_search_text)

    return faction_dict

def load_faction_mapping(faction_mapping_file="faction_mappings.txt"):
    """ Load the Faction ID to Faction Name mapping from a file """
    # Returns a dictionary, key of faction ID and value of faction name
    if Path(faction_mapping_file).is_file():
        with open(faction_mapping_file, 'r') as f:
            faction_dict = json.loads(f)
        return faction_dict
    else:
        return None

def download_unit_data(unit_link_list):
    """ Download unit data if we don't have it stored locally. """
    # Expecting dictionary 
    pass

def get_faction_id_mapping():
    faction_mapping = load_faction_mapping()
    if faction_mapping is None:
        faction_mapping = request_faction_id_mapping()
    return faction_mapping

def modify_unit_data():
    """ Take a list of unit data on disk and modify it """

    unit_data = get_single_unit_data("217", "bandersnatch-bndr-01a")
    # test transform
    print(unit_data)
    return 0
    
    faction_mapping = get_faction_id_mapping()
    unit_id_dict = get_unit_links(faction_id=faction_mapping["Draconis Combine"], era_id=13)
    unit_list = []
    i = 1
    for unit_id in unit_id_dict.keys():
        print(f"{i}/{len(unit_id_dict.keys())}: {unit_id}, {unit_id_dict[unit_id]}")
        # Get data from web or find on disk if present
        unit_data = get_single_unit_data(unit_id, unit_id_dict[unit_id], force=False)
        # do some transform
        # Write unit data to disk
        write_unit_data(unit_data, unit_data["unit_id"], unit_data["unit_linkname"], overwrite=True)
        i = i+1

def find_all_unique_specials(faction_name="Draconis Combine", era_id="13"):
    faction_mapping = get_faction_id_mapping()
    unit_id_dict = get_unit_links(faction_mapping[faction_name], era_id)
    unique_specials = []
    for unit_id in unit_id_dict.keys():
        unit_data = get_single_unit_data(unit_id, unit_id_dict[unit_id], force=False)
        specials_split = unit_data["specials"].split(',')
        for special_ability in specials_split:
            special_ability = special_ability.strip()
            if special_ability in unique_specials:
                continue
            else:
                unique_specials.append(special_ability)
    return unique_specials

    

def main():

    # ~ save_unit_links()
    # ~ link_dict = get_unit_links(linkfile="unitlinks.txt")
    faction_list = []
    faction_id_dict = get_faction_id_mapping()
    for faction_id in faction_id_dict.keys():
        faction_list.append(f"{faction_id_dict[faction_id]}: {faction_id}")
    for faction_name_and_id in sorted(faction_list):
        print(faction_name_and_id)
    print("")
    faction_id = input("[*] Enter faction ID: ")
    print(f"{faction_id_dict[faction_id]} selected")
    print("")

    era_id_dict = request_era_id_mapping(faction_id)
    for era_id in era_id_dict.keys():
        print(f"{era_id_dict[era_id]}: {era_id}")
    print("")
    era_id = input("[*] Enter Era ID: ")
    print(f"{era_id_dict[era_id]} selected")
    print("")

    # Download list of units
    link_dict = get_unit_links(faction_id, era_id)

    num_of_links = len(link_dict)
    i = 1

    outfile = f"AlphaStrike Unit Data, {faction_id_dict[faction_id]}, {era_id_dict[era_id]}.txt"

    with open(outfile, 'w') as f:
        for unit_id in link_dict.keys():
            print(f"{i}/{num_of_links}: {unit_id}")
            
            # Get the unit data, first checking cache before making request
            unit_data = get_unit_from_disk(unit_id, link_dict[unit_id])
            if not unit_data:
                # Data is not present on disk, download it
                unit_data = request_unit_info(unit_id, link_dict[unit_id])
                write_unit_data(unit_data)

            # Write the headers on the first iteration
            if i == 1:
                f.write(f"{convert_unit_data_to_csv(unit_data, headers=True)}\n")
                
            # Convert unit_data dict to CSV str
            unit_data_csv = convert_unit_data_to_csv(unit_data)
            # Write data to file
            f.write(f"{unit_data_csv}\n")
            # ~ print(unit_data_csv)
            
            i = i+1

def debug_function():

    print("This should not be found:")
    unit_data = request_unit_info(823,"danais")
    print(unit_data)

    print("This should have full data:")
    unit_data = request_unit_info(917,"dragonfly-viper-a")
    print(unit_data)


# ~ modify_unit_data()
# ~ print(find_all_unique_specials())
main()

# ~ debug_function()
# ~ eras = request_era_id_mapping(faction_id=34)
# ~ print(eras)


