# -- author : ceefar --
# -- project : nhs etl 2023 --

# -- imports --
import streamlit as st

# -- some handy objects --
JSON = int | str | float | bool | None | dict [str, "JSON"] | list["JSON"]
JSONobject = dict[str, JSON]
JSONList = list[JSON]

# -- general globals --
header = {"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36"}

# -- some misc funcs --
def st_page_load():
    """ self referencing af """
    st.set_page_config(layout="wide")

def get_cleaned_dept(user_department):
    if user_department == "Ear Nose and Throat":
        return "ent" 
    elif user_department == "Trauma and Orthopaedic":
        return "trauma orthopaedic"
    else:
        return user_department

def hex_to_rgb(hex_code):
    hex_code = hex_code.strip("#")  # Remove "#" if present
    r = int(hex_code[0:2], 16)
    g = int(hex_code[2:4], 16)
    b = int(hex_code[4:6], 16)
    return r, g, b

# -- misc handy classes --
class Misc:
    regions_list = {"midlands":"mids", "london":"london","north east and yorkshire":"ney", "south west":"swest", "east":"east", "south east":"seast", "north west":"nwest"}
    hospitals_regions = {'UNIVERSITY HOSPITALS BIRMINGHAM NHS FOUNDATION TRUST':"mids", 'CHESTERFIELD ROYAL HOSPITAL NHS FOUNDATION TRUST':"mids", 
                        'KETTERING GENERAL HOSPITAL NHS FOUNDATION TRUST':"mids", 'NOTTINGHAM UNIVERSITY HOSPITALS NHS TRUST':"mids", 
                        'SHERWOOD FOREST HOSPITALS NHS FOUNDATION TRUST':"mids", 'THE DUDLEY GROUP NHS FOUNDATION TRUST':"mids", 
                        'THE ROYAL ORTHOPAEDIC HOSPITAL NHS FOUNDATION TRUST':"mids", 'THE SHREWSBURY AND TELFORD HOSPITAL NHS TRUST':"mids", 
                        'UNIVERSITY HOSPITALS OF DERBY AND BURTON NHS FOUNDATION TRUST':"mids", 'UNIVERSITY HOSPITALS OF NORTH MIDLANDS NHS TRUST':"mids", 
                        'WORCESTERSHIRE ACUTE HOSPITALS NHS TRUST':"mids", 'WYE VALLEY NHS TRUST':"mids", 'WALSALL HEALTHCARE NHS TRUST':"mids", 
                        "BIRMINGHAM WOMEN'S AND CHILDREN'S NHS FOUNDATION TRUST":"mids", 'GEORGE ELIOT HOSPITAL NHS TRUST':"mids", 
                        'NORTHAMPTON GENERAL HOSPITAL NHS TRUST':"mids", 'SANDWELL AND WEST BIRMINGHAM HOSPITALS NHS TRUST':"mids", 
                        'SOUTH WARWICKSHIRE UNIVERSITY NHS FOUNDATION TRUST':"mids", 'THE ROBERT JONES AND AGNES HUNT ORTHOPAEDIC HOSPITAL NHS FOUNDATION TRUST':"mids", 
                        'THE ROYAL WOLVERHAMPTON NHS TRUST':"mids", 'UNITED LINCOLNSHIRE HOSPITALS NHS TRUST':"mids", 
                        'UNIVERSITY HOSPITALS COVENTRY AND WARWICKSHIRE NHS TRUST':"mids", 'UNIVERSITY HOSPITALS OF LEICESTER NHS TRUST':"mids",
                        'DORSET COUNTY HOSPITAL NHS FOUNDATION TRUST':"swest", 'GREAT WESTERN HOSPITALS NHS FOUNDATION TRUST':"swest", 
                        'ROYAL CORNWALL HOSPITALS NHS TRUST':"swest", 'ROYAL UNITED HOSPITALS BATH NHS FOUNDATION TRUST':"swest", 'SOMERSET NHS FOUNDATION TRUST':"swest",
                        'UNIVERSITY HOSPITALS BRISTOL AND WESTON NHS FOUNDATION TRUST':"swest", 'UNIVERSITY HOSPITALS PLYMOUTH NHS TRUST':"swest", 
                        'GLOUCESTERSHIRE HOSPITALS NHS FOUNDATION TRUST':"swest", 'NORTH BRISTOL NHS TRUST':"swest", 
                        'ROYAL DEVON UNIVERSITY HEALTHCARE NHS FOUNDATION TRUST':"swest", 'SALISBURY NHS FOUNDATION TRUST':"swest", 
                        'TORBAY AND SOUTH DEVON NHS FOUNDATION TRUST':"swest", 'UNIVERSITY HOSPITALS DORSET NHS FOUNDATION TRUST':"swest", 
                        'YEOVIL DISTRICT HOSPITAL NHS FOUNDATION TRUST':"swest",
                        'BARTS HEALTH NHS TRUST':"london", 'CROYDON HEALTH SERVICES NHS TRUST':"london", 'GREAT ORMOND STREET HOSPITAL FOR CHILDREN NHS FOUNDATION TRUST':"london",
                        'HOMERTON HEALTHCARE NHS FOUNDATION TRUST':"london", "KING'S COLLEGE HOSPITAL NHS FOUNDATION TRUST":"london", 'LEWISHAM AND GREENWICH NHS TRUST':"london",
                        'MOORFIELDS EYE HOSPITAL NHS FOUNDATION TRUST':"london", 'ROYAL FREE LONDON NHS FOUNDATION TRUST':"london", 
                        "ST GEORGE'S UNIVERSITY HOSPITALS NHS FOUNDATION TRUST":"london", 'UNIVERSITY COLLEGE LONDON HOSPITALS NHS FOUNDATION TRUST':"london",
                        'BARKING, HAVERING AND REDBRIDGE UNIVERSITY HOSPITALS NHS TRUST':"london", 'CHELSEA AND WESTMINSTER HOSPITAL NHS FOUNDATION TRUST':"london", 
                        'EPSOM AND ST HELIER UNIVERSITY HOSPITALS NHS TRUST':"london", "GUY'S AND ST THOMAS' NHS FOUNDATION TRUST":"london", 
                        'IMPERIAL COLLEGE HEALTHCARE NHS TRUST':"london", 'KINGSTON HOSPITAL NHS FOUNDATION TRUST':"london", 
                        'LONDON NORTH WEST UNIVERSITY HEALTHCARE NHS TRUST':"london", 'NORTH MIDDLESEX UNIVERSITY HOSPITAL NHS TRUST':"london", 
                        'ROYAL NATIONAL ORTHOPAEDIC HOSPITAL NHS TRUST':"london", 'THE HILLINGDON HOSPITALS NHS FOUNDATION TRUST':"london", 
                        'WHITTINGTON HEALTH NHS TRUST':"london",
                        'BARNSLEY HOSPITAL NHS FOUNDATION TRUST':"ney", 'CALDERDALE AND HUDDERSFIELD NHS FOUNDATION TRUST':"ney", 
                        'DONCASTER AND BASSETLAW TEACHING HOSPITALS NHS FOUNDATION TRUST':"ney", 'HARROGATE AND DISTRICT NHS FOUNDATION TRUST':"ney", 
                        'LEEDS TEACHING HOSPITALS NHS TRUST':"ney", 'THE NEWCASTLE UPON TYNE HOSPITALS NHS FOUNDATION TRUST':"ney", 
                        'NORTH TEES AND HARTLEPOOL NHS FOUNDATION TRUST':"ney", 'NORTHUMBRIA HEALTHCARE NHS FOUNDATION TRUST':"ney", 
                        'SHEFFIELD TEACHING HOSPITALS NHS FOUNDATION TRUST':"ney", 'SOUTH TYNESIDE AND SUNDERLAND NHS FOUNDATION TRUST':"ney", 
                        'YORK AND SCARBOROUGH TEACHING HOSPITALS NHS FOUNDATION TRUST':"ney", 'AIREDALE NHS FOUNDATION TRUST':"ney", 
                        'BRADFORD TEACHING HOSPITALS NHS FOUNDATION TRUST':"ney", 'COUNTY DURHAM AND DARLINGTON NHS FOUNDATION TRUST':"ney", 
                        'GATESHEAD HEALTH NHS FOUNDATION TRUST':"ney", 'HULL UNIVERSITY TEACHING HOSPITALS NHS TRUST':"ney", 'MID YORKSHIRE TEACHING NHS TRUST':"ney", 
                        'NORTH CUMBRIA INTEGRATED CARE NHS FOUNDATION TRUST':"ney", 'NORTHERN LINCOLNSHIRE AND GOOLE NHS FOUNDATION TRUST':"ney", 
                        'SOUTH TEES HOSPITALS NHS FOUNDATION TRUST':"ney", 'THE ROTHERHAM NHS FOUNDATION TRUST':"ney",
                        'BUCKINGHAMSHIRE HEALTHCARE NHS TRUST':"seast", 
                        'EAST KENT HOSPITALS UNIVERSITY NHS FOUNDATION TRUST':"seast", 
                        'FRIMLEY HEALTH NHS FOUNDATION TRUST':"seast",
                        'ISLE OF WIGHT NHS TRUST':"seast",
                        'MEDWAY NHS FOUNDATION TRUST':"seast", 
                        'PORTSMOUTH HOSPITALS UNIVERSITY NATIONAL HEALTH SERVICE TRUST':"seast",
                        'ROYAL BERKSHIRE NHS FOUNDATION TRUST':"seast", 
                        'SURREY AND SUSSEX HEALTHCARE NHS TRUST':"seast", 
                        'UNIVERSITY HOSPITALS SUSSEX NHS FOUNDATION TRUST':"seast",
                        "ASHFORD AND ST PETER'S HOSPITALS NHS FOUNDATION TRUST":"seast",
                        'DARTFORD AND GRAVESHAM NHS TRUST':"seast",
                        'EAST SUSSEX HEALTHCARE NHS TRUST':"seast",
                        'HAMPSHIRE HOSPITALS NHS FOUNDATION TRUST':"seast", 
                        'MAIDSTONE AND TUNBRIDGE WELLS NHS TRUST':"seast",
                        'OXFORD UNIVERSITY HOSPITALS NHS FOUNDATION TRUST':"seast",
                        'QUEEN VICTORIA HOSPITAL NHS FOUNDATION TRUST':"seast", 
                        'ROYAL SURREY COUNTY HOSPITAL NHS FOUNDATION TRUST':"seast", 
                        'UNIVERSITY HOSPITAL SOUTHAMPTON NHS FOUNDATION TRUST':"seast",                                                
                        "ALDER HEY CHILDREN'S NHS FOUNDATION TRUST":"nwest", 
                        'BOLTON NHS FOUNDATION TRUST':"nwest", 
                        'EAST CHESHIRE NHS TRUST':"nwest", 
                        'LANCASHIRE TEACHING HOSPITALS NHS FOUNDATION TRUST':"nwest",
                        'LIVERPOOL UNIVERSITY HOSPITALS NHS FOUNDATION TRUST':"nwest", 
                        'MANCHESTER UNIVERSITY NHS FOUNDATION TRUST':"nwest",
                        'NORTHERN CARE ALLIANCE NHS FOUNDATION TRUST':"nwest", 
                        'ST HELENS AND KNOWSLEY TEACHING HOSPITALS NHS TRUST':"nwest", 
                        'TAMESIDE AND GLOSSOP INTEGRATED CARE NHS FOUNDATION TRUST':"nwest", 
                        'UNIVERSITY HOSPITALS OF MORECAMBE BAY NHS FOUNDATION TRUST':"nwest", 
                        'WIRRAL UNIVERSITY TEACHING HOSPITAL NHS FOUNDATION TRUST':"nwest", 
                        'BLACKPOOL TEACHING HOSPITALS NHS FOUNDATION TRUST':"nwest",
                        'COUNTESS OF CHESTER HOSPITAL NHS FOUNDATION TRUST':"nwest",
                        'EAST LANCASHIRE HOSPITALS NHS TRUST':"nwest", 
                        'LIVERPOOL HEART AND CHEST HOSPITAL NHS FOUNDATION TRUST':"nwest", 
                        "LIVERPOOL WOMEN'S NHS FOUNDATION TRUST":"nwest",
                        'MID CHESHIRE HOSPITALS NHS FOUNDATION TRUST':"nwest", 
                        'SOUTHPORT AND ORMSKIRK HOSPITAL NHS TRUST':"nwest", 
                        'STOCKPORT NHS FOUNDATION TRUST':"nwest",
                        'THE WALTON CENTRE NHS FOUNDATION TRUST':"nwest", 
                        'WARRINGTON AND HALTON TEACHING HOSPITALS NHS FOUNDATION TRUST':"nwest",
                        'WRIGHTINGTON, WIGAN AND LEIGH NHS FOUNDATION TRUST':"nwest",                                 
                        'BEDFORDSHIRE HOSPITALS NHS FOUNDATION TRUST':"east", 
                        'EAST AND NORTH HERTFORDSHIRE NHS TRUST':"east", 
                        'JAMES PAGET UNIVERSITY HOSPITALS NHS FOUNDATION TRUST':"east", 
                        'MILTON KEYNES UNIVERSITY HOSPITAL NHS FOUNDATION TRUST':"east",
                        'NORTH WEST ANGLIA NHS FOUNDATION TRUST':"east", 
                        'THE PRINCESS ALEXANDRA HOSPITAL NHS TRUST':"east",
                        'WEST HERTFORDSHIRE TEACHING HOSPITALS NHS TRUST':"east", 
                        'CAMBRIDGE UNIVERSITY HOSPITALS NHS FOUNDATION TRUST':"east", 
                        'EAST SUFFOLK AND NORTH ESSEX NHS FOUNDATION TRUST':"east", 
                        'MID AND SOUTH ESSEX NHS FOUNDATION TRUST':"east", 
                        'NORFOLK AND NORWICH UNIVERSITY HOSPITALS NHS FOUNDATION TRUST':"east", 
                        'ROYAL PAPWORTH HOSPITAL NHS FOUNDATION TRUST':"east",
                        "THE QUEEN ELIZABETH HOSPITAL, KING'S LYNN, NHS FOUNDATION TRUST":"east",
                        'WEST SUFFOLK NHS FOUNDATION TRUST':"east"}
    departments_list = [
        'General Surgery',
        'Urology',
        'Trauma and Orthopaedic',
        'Ear Nose and Throat',
        'Ophthalmology',
        'Oral Surgery',
        'Neurosurgical',
        'Plastic Surgery',
        'Cardiothoracic Surgery',
        'General Internal Medicine',
        'Gastroenterology',
        'Cardiology',
        'Dermatology',
        'Respiratory Medicine',
        'Neurology',
        'Rheumatology',
        'Elderly Medicine',
        'Gynaecology']
    
# @dataclass
class NHSColors:
    NHS_Blue: str = "#005EB8"
    NHS_Dark_Blue: str = "#003087"
    NHS_Light_Blue: str = "#0072CE"
    NHS_Yellow: str = "#FFB81C"
    NHS_Dark_Yellow: str = "#FF9900"
    NHS_Light_Yellow: str = "#FFD400"
    NHS_Green: str = "#00A499"
    NHS_Dark_Green: str = "#00703C"
    NHS_Light_Green: str = "#009A44"
    NHS_Pink: str = "#ED008C"
    NHS_Purple: str = "#660099"
    NHS_Orange: str = "#FF6600"
    NHS_Teal: str = "#009999"

