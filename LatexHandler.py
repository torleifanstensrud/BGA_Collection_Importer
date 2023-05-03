import os
import subprocess
from Collection import BoardGame #To access NO_VALUE
from math import ceil

class LatexHandler:
    def __init__(self, collection, relative_path, filename):
        self.collection = collection
        self.latex_path = relative_path
        self.latex_filename = filename

    def write_preamble(self):
        with open(self.latex_path+self.latex_filename,"w",  encoding="utf-8") as latex_file:
            # Write documentclass
            latex_file.write('\\documentclass[twoside, a4paper, 10pt]{report}\n')
            
            # Write packages
            latex_file.write(
                            '\\usepackage[utf8]{inputenc}\n'
                            '\\usepackage{slantsc}\n'
                            '\\usepackage{lmodern}\n'
                            '\n'
                            '\\usepackage{fullpage}\n'
                            '\n'
                            '\\usepackage{longtable}\n'
                            '\\usepackage{tabularx}\n'
                            '\\usepackage{array}\n'
                            '\\usepackage{caption}\n'
                            '\\usepackage{booktabs}\n'
                            '\\usepackage{arydshln}\n'
                            '\\usepackage[figuresright]{rotating}\n'
                            '\\usepackage{multirow}\n'
                            '\n'
                            '\\usepackage{color, colortbl}\n'
                            '\\definecolor{LightGray}{gray}{0.9}\n'
                            '\n'
                            '\\usepackage{titlesec}\n'
                            '\\titleformat{\\section}[hang]\n'
                            '  {}\n'
                            '  {}\n'
                            '  {0em}\n'
                            '  {\\Huge\\bf\\center}\n'
                            '\n'
                            '\\usepackage{fancyhdr}\n'
                            '\\pagestyle{fancy}\n'
                            '\\fancyhead{}\n'
                            '\\fancyfoot{}\n'
                            '\\fancyfoot[RO] {Page \\thepage}\n'
                            '\\fancyfoot[LE] {Page \\thepage}\n'
                            '\\fancyfoot[C] {\\leftmark}\n'
                            '\\renewcommand{\\headrulewidth}{0pt}\n'
                            '\\renewcommand{\\footrulewidth}{0.4pt}\n'
                            '\\renewcommand\\sectionmark[1]{\\markboth{#1}{}}\n'
                            '\n'
                            )
            
            # Write begin document
            latex_file.write(
                            '\\begin{document}\n'
                            )
            
            # Write column definition
            latex_file.write(
                            '\\newcolumntype{+}{>{\\global\\let\\currentrowstyle\\relax}}\n'
                            '\\newcolumntype{^}{>{\\currentrowstyle}}\n'
                            '\\newcommand{\\rowstyle}[1]{\\gdef\\currentrowstyle{#1}#1}\n'
                            '\\newcolumntype{P}[1]{>{\\centering\\arraybackslash}p{#1}}\n'
                            '\\newcolumntype{Y}{>{\\centering\\arraybackslash}X}\n'
                            )
            
    def write_player_count_tables(self, max_player_count=100):
        with open(self.latex_path+self.latex_filename,"a", encoding="utf-8") as latex_file:            
            # Define table header
            header_string = (
                            '\\renewcommand{\\arraystretch}{1.1}\\\\\n'
                            '\\hline\n'
                            '\\scshape Board game title  &\\scshape Avg.({\\slshape min.}) & \\scshape BGG Rank\\\\\n'
                            '\\hline\n'
                            '\\endfirsthead\n'
                            '\\scshape Board game title  &\\scshape Avg.({\\slshape min.}) & \\scshape BGG Rank \\\\\n'
                            '\\hline\n'
                            '\\endhead\n')
            
            valid_player_counts = [player_count for player_count in self.collection.player_counts.keys() if int(player_count) <= max_player_count]
            for player_count in sorted(valid_player_counts):       
                if(player_count == 1):
                    player_string = 'Solo play'
                else:
                    player_string = str(player_count) + ' Players'

                latex_file.write('\\section{' + player_string + '} \n')
                latex_file.write('\\setcounter{page}{1}\n')
                        
                for player_type in ['optimal', 'recommended']:
                    
                    # Check if there are games with that player count for the player count type
                    if self.collection.player_counts[player_count][player_type]:
                        # Write table header
                        latex_file.write(
                                        '\\begin{longtable}{+p{10cm}^c^c^c}\n'
                                        '\\caption*{\\large \\textbf{' + player_type.capitalize() + ' for}}\n'
                                        + header_string
                                        )
                        
                        row_counter = 1
                        for base_game_id in self.collection.ids_sorted_by_playing_time(self.collection.player_counts[player_count][player_type].keys()):
                            if row_counter % 2:
                                latex_file.write('\\rowcolor{LightGray}')                                
                               
                            base_game = self.collection.base_games[base_game_id]
                             
                            if self.collection.player_counts[player_count][player_type][base_game_id]['need_expansion']:
                                row_string = base_game.get_latex_string('Parenthesis', 'Playing Time', 'BGG Rank')
                            else:
                                row_string = base_game.get_latex_string('Playing Time', 'BGG Rank')    
                            latex_file.write(row_string)
                            
                            # Write applicable expansions for player count
                            for expansion_id in self.collection.player_counts[player_count][player_type][base_game_id]['expansions']:
                                if row_counter % 2:
                                    latex_file.write('\\rowcolor{LightGray}')  
#                                row_counter += 1
                                
                                expansion = self.collection.expansions[expansion_id]
                                row_string = expansion.get_latex_string('Playing Time', '')  
                                latex_file.write(row_string)
                                
                            row_counter += 1
                        # Write end table
                        latex_file.write('\\hline\n\\end{longtable}\n')
                    
                latex_file.write('\\cleardoublepage\n')

    def write_game_history(self):
        with open(self.latex_path+self.latex_filename,"a", encoding="utf-8") as latex_file:
            latex_file.write('\\pagestyle{empty}\n')
            
            for base_game_id in self.collection.ids_sorted_by_title(self.collection.base_games.keys()):
                base_game = self.collection.base_games[base_game_id]
                
                if base_game.playing_time > BoardGame.NO_VALUE:
                    pass
                else:
                    for page_index in range(2):
                        latex_file.write(
                                        '\\begin{sidewaystable} \n' 
                                        '\\subsection*{' + base_game.get_latex_title() + '}\n'
                                        )
                    
                        if base_game.expansions:
                            latex_file.write( 
                                            'Available expansions:\n'
                                            '\\begin{enumerate}\n'
                                            )
                            for expansion_id in base_game.expansions:
                                expansion = self.collection.expansions[expansion_id]
                                latex_file.write('\\item ' + expansion.get_latex_title() + '\n')        
    
                            latex_file.write('\\end{enumerate}\n')   
        
                        
                        latex_file.write(
                                        '{\\def\\arraystretch{2}\\tabcolsep=10pt\n'
                                        '\\begin{tabularx}{\\textwidth}{|P{30pt}|' + 'c|'*len(base_game.expansions) + 'Y|P{60pt}|c|}\n'
                                        '\\multicolumn{1}{c}{}'                                    
                                        )
    
                        if base_game.expansions:
                            latex_file.write(' & \\multicolumn{' + str(len(base_game.expansions)) + '}{c}{\\makebox[0pt]{Expansions}}')
                            
                        latex_file.write(
                                        '& \\multicolumn{1}{c}{}& \\multicolumn{2}{c}{Winner} \\\\ \n'
                                        '\\hline \n'
                                        'Date &'
                                        )
                        for index in range(len(base_game.expansions)):
                            latex_file.write(str(index+1) + ' & ')
    
                        latex_file.write(
                                        'Players & Name & Score\\\\ \n'
                                        '\\hline \n'
                                        )
                        
                        multicolumn_row_string = '\\multirow{ 2}{*}{} & '
                        blank_row_string = ' &'
                        for index in range(len(base_game.expansions)):
                            multicolumn_row_string = multicolumn_row_string + ' \\multirow{ 2}{*}{} &'
                            blank_row_string = blank_row_string + ' &'
        
                        multicolumn_row_string = multicolumn_row_string + ' & \\multirow{ 2}{*}{} & \\multirow{ 2}{*}{} \\\\ \n'
                        
                        offset = len(base_game.expansions)
                        multicolumn_row_string = multicolumn_row_string + '\\cdashline{' + str(2+offset) + '-' + str(2+offset) + '}[1pt/2pt]\n'
                        
                        blank_row_string = blank_row_string + ' & & \\\\ \n'
                        blank_row_string = blank_row_string + '\\hline \n'
                        
                        MAX_GAME_ROWS = 9
                        N_plays = MAX_GAME_ROWS-ceil(len(base_game.expansions)/2);
                        for index in range(N_plays):
                            latex_file.write( multicolumn_row_string)
                            latex_file.write(blank_row_string)
                        
                        latex_file.write(
                                        '\\end{tabularx}} \n' 
                                        '\\end{sidewaystable} \n' 
                                        )      
                        if page_index == 0:
                            latex_file.write('\clearpage \n')
                        else:
                            latex_file.write('\\cleardoublepage \n')

    def create_tex(self):
        self.write_preamble()
        self.write_player_count_tables(6)
        self.write_game_history()
        
        with open(self.latex_path+self.latex_filename,"a", encoding="utf-8") as latex_file:
            latex_file.write('\\end{document}')
            
    def compile_latex(self):
        subprocess.check_call('pdflatex -output-directory ' + self.latex_path + ' ' + self.latex_path + self.latex_filename, shell=False)
        os.remove(self.latex_path + self.latex_filename.split('.')[0] + '.log')
        os.remove(self.latex_path + self.latex_filename.split('.')[0] + '.aux')
    
    