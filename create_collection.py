from BoardGameGeekAPI import BoardGameGeekAPI
from Collection import Collection
from LatexHandler import LatexHandler

api = BoardGameGeekAPI('Cyduck')
       
# Import collection from BGG 
collection = Collection()  
xml_collection = api.query_bgg_collection()      
game_ids = collection.parse_xml_collection(xml_collection)

load_from_file = False
if load_from_file:
    collection.import_xml_games()
    
else:
    xml_games = api.query_bgg_ids(game_ids)
    collection.export_xml_games(xml_games)
    collection.parse_xml_games(xml_games)

# Create PDF
latex_path = "../Latex/"
latex_filename = "collection.tex"
latex = LatexHandler(collection, latex_path, latex_filename) 
latex.create_tex()
#latex.compile_latex()