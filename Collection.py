import pickle

class BoardGame:
    NO_VALUE = 1000000 # Ensures the appropriate field will be sorted last
    
    def __init__(self, bgg_id):
        self.title = ''
        self.bgg_id = bgg_id  
        self.min_players = 0
        self.max_players = 0
        self.playing_time = 0
        self.optimal_player_count = []
        self.recommended_player_count = []
        
    def __repr__(self):
        return self.title + ' (' + self.bgg_id + ')'
    
    def set_title(self, raw_title):
        self.title = raw_title.replace('–','-') # Replace non-UTF-8 dash character 
    
    def get_latex_string(self, *args):
        info_string = ''
        info_string_part = ''
        
        for arg in args:  
            if arg == 'BGG Rank':
                if self.bgg_rank == self.NO_VALUE:
                    info_string_part = ' & -'
                else:
                    info_string_part = ' & ' + str(self.bgg_rank)
            
            elif arg == 'Playing Time':
                if self.playing_time == self.NO_VALUE:
                    info_string_part = ' & -'
                else:
                    info_string_part = ' & ' + str(self.playing_time)
        
            elif arg == '':
                info_string_part = ' & '
            else:
                info_string_part = ''
            
            info_string = info_string + info_string_part
        
#        line_string = '\\hdashline[0.5pt/5pt]'
        suffix = '\\\\\n'# + line_string
        return info_string + suffix
    
    def add_info_from_xml(self, xml_item):
        title = xml_item.find('.//name[@type="primary"]').get('value')
        self.set_title(title)
        
        # Statistics
        min_players = int(xml_item.find('.//minplayers').get('value'))
        max_players = int(xml_item.find('.//maxplayers').get('value'))
        playing_time = int(xml_item.find('.//playingtime').get('value'))
        if playing_time == 0:
            playing_time = self.NO_VALUE
        
        self.min_players = min_players
        self.max_players = max_players
        self.playing_time = playing_time
        
        # Determining best and recommended players
        poll = xml_item.find('.//poll[@name="suggested_numplayers"]')
        
        for results in poll:
            if results.getchildren():
                player_count = results.attrib['numplayers']
                
                if player_count.isdigit(): # Ignores entries with '4+', '7+', etc
                    player_count = int(player_count)
                    
                    votes = dict()
                    votes['optimal'] = int(results.find('./result[@value="Best"]').get('numvotes'))
                    votes['recommended'] = int(results.find('./result[@value="Recommended"]').get('numvotes'))
                    votes['not_recommended'] = int(results.find('./result[@value="Not Recommended"]').get('numvotes'))
                              
                    winner = max(votes, key=votes.get)
                    
                    if(winner == 'optimal'):
                        self.optimal_player_count.append(player_count)
                    elif(winner == 'recommended'):
                        self.recommended_player_count.append(player_count)
            else:
                # Users haven't voted on player count
                self.recommended_player_count = list(range(int(min_players), int(max_players)+1))
        

class BaseGame(BoardGame):
    def __init__(self, bgg_id):
        BoardGame.__init__(self, bgg_id)
        self.bgg_rank = self.NO_VALUE
        self.expansions = dict()
        
    def __repr__(self):
        summary = BoardGame.__repr__(self)
        for expansion_id in self.expansions:
            summary += '\n\t' + self.expansions[expansion_id].short_title + ' (' + expansion_id + ')'
            
        return summary
      
    def get_latex_title(self):
        return self.title.replace('&', '\&')   
    
    def get_latex_string(self, *args):     
        title = self.get_latex_title()
        
        if 'Parenthesis' in args:
            title = '(' + title + ')'

        info_string = BoardGame.get_latex_string(self, *args)

        return title + info_string
    
    def add_info_from_xml(self, xml_item):
        BoardGame.add_info_from_xml(self, xml_item)
        rank_string = xml_item.find('.//rank[@friendlyname="Board Game Rank"]').get('value')
        if rank_string.isdigit():
            self.bgg_rank = int(rank_string)
        else:
            self.bgg_rank = self.NO_VALUE

    def add_expansion(self, expansion):
        self.expansions[expansion.bgg_id] = expansion
    
class Expansion(BoardGame):
    def __init__(self, bgg_id):
        BoardGame.__init__(self, bgg_id)
        self.short_title = self.title
        self.base_game_id = None
        
    def get_latex_title(self):
        return self.short_title.replace('&', '\&')   
    
    def get_latex_string(self, *args):     
        title = self.get_latex_title()    
        prefix = '\\quad \\textit{' + title + '}' 

        info_string = BoardGame.get_latex_string(self, *args)

        return prefix + info_string
    
    def add_info_from_xml(self, xml_item, base_game_ids):
        BoardGame.add_info_from_xml(self, xml_item)
        
        links = xml_item.findall('.//link[@type="boardgameexpansion"][@inbound="true"]')
        for link in links:
            base_game_id = link.attrib['id']
            if base_game_id in base_game_ids:
                return base_game_id
        return None
        
    def set_short_title(self, base_game_title):
        length_shared_title = 0
        for char_self, char_base in zip(self.title, base_game_title):
            if(char_self==char_base):
                length_shared_title += 1
            else:
                break
        if length_shared_title > 1: # Ensures that more than just the first character matches
            self.short_title = self.title[length_shared_title:].strip(' :-–')
            
        self.latex_short_title = '\\quad\\textit{' + self.short_title.replace('&', '\&') + '}'
        
class Collection:
    def __init__(self):
        self.base_games = dict()
        self.expansions = dict()
        self.player_counts = dict()
        self.xml_games_filename = 'xml_games.pkl'
        
    def __repr__(self):
        summary= ''
        for game in self.base_games:
            summary += str(self.base_games[game]) + '\n'
        return summary
        
    def parse_xml_collection(self, xml_collection):
        base_game_ids = []
        for item in xml_collection['base_game_items']:
            bgg_id = item.attrib['objectid']
            base_game = BaseGame(bgg_id)
            
            self.base_games[base_game.bgg_id] = base_game
            base_game_ids.append(bgg_id)
            
        expansion_ids = []
        for item in xml_collection['expansion_items']:
            bgg_id = item.attrib['objectid']
            expansion = Expansion(bgg_id)
                
            self.expansions[expansion.bgg_id] = expansion
            expansion_ids.append(bgg_id)
        
        game_ids = {
                'base_game_ids': base_game_ids,
                'expansion_ids': expansion_ids,
                }
        
        return game_ids
    
    def export_xml_games(self, xml_games):
        xml_games_file = open(self.xml_games_filename, "wb")
        pickle.dump(xml_games, xml_games_file)
        xml_games_file.close()
        
    def import_xml_games(self):
        xml_games_file = open(self.xml_games_filename, "rb")
        xml_games = pickle.load(xml_games_file)
        self.parse_xml_games(xml_games)
        
    def parse_xml_games(self, xml_games):
        print('Parsing base games:')
        for bgg_id in xml_games['xml_base_games']:
            item = xml_games['xml_base_games'][bgg_id][0]
            self.base_games[bgg_id].add_info_from_xml(item)
            self.update_player_counts_base_game(bgg_id)
            print("\t" + self.base_games[bgg_id].title + ' (' + bgg_id + ')')
        
        print('Parsing expansions:')
        for bgg_id in xml_games['xml_expansions']:
            item = xml_games['xml_expansions'][bgg_id][0]
            base_game_id = self.expansions[bgg_id].add_info_from_xml(item, list(self.base_games))
            print("\t" + self.expansions[bgg_id].title + ' (' + bgg_id + ')')
            
            # Add expansion to base game 
            if base_game_id:
                self.base_games[base_game_id].add_expansion(self.expansions[bgg_id])
                self.expansions[bgg_id].base_game_id = base_game_id
                self.expansions[bgg_id].set_short_title(self.base_games[base_game_id].title)
                
            self.update_player_counts_expansion(bgg_id)
        
    def update_player_counts_base_game(self, bgg_id):
        base_game = self.base_games[bgg_id]
        
        optimal_player_count = base_game.optimal_player_count
        recommended_player_count = base_game.recommended_player_count
        
        for player_count in optimal_player_count:
            if not self.player_counts.get(player_count):
                self.player_counts[player_count] = {'optimal': dict(), 'recommended': dict()}
            self.player_counts[player_count]['optimal'][bgg_id] = {'need_expansion': False, 'expansions': []}
            
        for player_count in recommended_player_count:
            if not self.player_counts.get(player_count):
                self.player_counts[player_count] = {'optimal': dict(), 'recommended': dict()}
            self.player_counts[player_count]['recommended'][bgg_id] = {'need_expansion': False, 'expansions': []}
          
    def update_player_counts_expansion(self, bgg_id):
        expansion = self.expansions[bgg_id]
        base_game = self.base_games[expansion.base_game_id]
        
        optimal_player_count = expansion.optimal_player_count
        recommended_player_count = expansion.recommended_player_count
        
        for player_count in optimal_player_count:
            if not self.player_counts.get(player_count):
                    self.player_counts[player_count] = {'optimal': dict(), 'recommended': dict()}
            if player_count not in base_game.optimal_player_count:
                self.player_counts[player_count]['optimal'][base_game.bgg_id] = {'need_expansion': True, 'expansions': [bgg_id]}
            else:
                self.player_counts[player_count]['optimal'][base_game.bgg_id]['expansions'].append(bgg_id)
            
        for player_count in recommended_player_count:
            if not self.player_counts.get(player_count):
                    self.player_counts[player_count] = {'optimal': dict(), 'recommended': dict()}
            if player_count not in base_game.recommended_player_count:
                self.player_counts[player_count]['recommended'][base_game.bgg_id] = {'need_expansion': True, 'expansions': [bgg_id]}
            else:
                self.player_counts[player_count]['recommended'][base_game.bgg_id]['expansions'].append(bgg_id)
                
    def ids_sorted_by_title(self, base_game_ids):
        return sorted(base_game_ids, key=lambda base_game_id: self.base_games[base_game_id].title)
    
    def ids_sorted_by_playing_time(self, base_game_ids):
        return sorted(base_game_ids, key=lambda base_game_id: (self.base_games[base_game_id].playing_time, self.base_games[base_game_id].title))
    
    def ids_sorted_by_bgg_rank(self, base_game_ids):
        return sorted(base_game_ids, key=lambda base_game_id: (self.base_games[base_game_id].bgg_rank, self.base_games[base_game_id].title))