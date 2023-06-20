#install unidecode on command line using pip install Unidecode
from unidecode import unidecode

import pandas as pd
import numpy as np
import re

def get_player_stats(player_id, def_id, bball_ref, nba_id): #get stats (offensive for now ...?)

    stats = [None,None,None, None, None] #FGA per 100, FG%, 3PFG%, ORAT, DRAT OF DEFENDER

    #FIND PLAYER NAME from nba_id
    nba_id_col = 7 #player ID
    bref_name_col = 0 #BREF NAME
    #import pdb; pdb.set_trace()
    nba_row = nba_id.index[nba_id['NBAID'] == player_id] # extract the row of the player
    nba_row = nba_row.tolist()
    nba_row = nba_row[0]

    def_row = nba_id.index[nba_id['NBAID'] == player_id]  # extract the row of the defender!
    def_row = def_row.tolist()
    def_row = def_row[0] #to int

    player_name = nba_id.iloc[nba_row, bref_name_col] #name as listed on bball reference table

    def_name = nba_id.iloc[def_row, bref_name_col]


    fga = 8
    fg = 9
    tp = 12
    orat = 29
    drat = 30

    row = bball_ref.index[bball_ref["Player"] == player_name]
    row = row.tolist()

    drow = bball_ref.index[bball_ref["Player"] == def_name]
    drow = drow.tolist()
    if drow:
        drow = drow[0] -1 # indexes are off by one for some reason..?
        stats[4] = bball_ref.iloc[drow, drat]

    if row: #if not empty
        row = row[0] -1
        stats[0] = bball_ref.iloc[row, fga]
        stats[1] = bball_ref.iloc[row, fg]
        stats[2] = bball_ref.iloc[row, tp]
        stats[3] = bball_ref.iloc[row, orat]

    return stats


def main():
    pandas_matrix = pd.read_csv("shot_logs.csv")

    n = pandas_matrix.shape[0]
    m = pandas_matrix.shape[1]

    #get shot ---> get player ID ---> get player name --> get player stats (?)

    numpy_matrix = pandas_matrix.to_numpy()  # same structure as numpy matrix
    nba_id = pd.read_csv("nba_id.csv",encoding = 'utf-8-sig', header = 0, nrows = 4293, index_col = False) # get player IDs from name
    for column in nba_id.columns:  # Need to remove Byte Order Marker at beginning of first column name
        new_column_name = re.sub(r"[^0-9a-zA-Z.,-/_ ]", "", column)
        nba_id.rename(columns={column: new_column_name}, inplace=True)


    bball_ref = pd.read_csv("bball_ref.csv", header = 0, index_col = 0)

    for i in range(len(bball_ref)): #remove asterisks!
        bball_ref.iloc[i,1] = unidecode(nba_id.iloc[i,1]) #unidecode
        final_string = re.sub("\*", '', bball_ref.iloc[i,1]) #regex substitution!
        bball_ref.iloc[i,1] = final_string


    ids = pandas_matrix["player_id"]
    d_ids = pandas_matrix["CLOSEST_DEFENDER_PLAYER_ID"]

    new_cols = np.zeros((n,5)) #5 is the current number of new features we are adding

    for i in range(n):
        stats = get_player_stats(ids[i], d_ids[i], bball_ref, nba_id)
        new_cols[i,:] = stats


    w_col = pandas_matrix["W"].to_numpy()
    w_binary = w_col == "W"
    w_binary = w_binary * 1
    pandas_matrix["W"] = w_binary

    home_col = pandas_matrix["LOCATION"].to_numpy()
    home_binary = home_col == "H"
    home_binary = home_binary * 1
    pandas_matrix["LOCATION"] = home_binary

    pts_col = pandas_matrix["PTS_TYPE"].to_numpy()
    pts_binary = pts_col == 3
    pts_binary = pts_binary * 1 #1 if 3 pt shot, 0 if 2 pt shot
    pandas_matrix["PTS_TYPE"] = pts_binary



    pandas_matrix["FGA"] = new_cols[:,0]
    pandas_matrix["FG percent"] = new_cols[:,1]
    pandas_matrix["Three Point"] = new_cols[:,2]
    pandas_matrix["ORAT"] = new_cols[:,3]
    pandas_matrix["DRAT"] = new_cols[:,4]

    pandas_matrix.drop(columns = ["GAME_ID","player_id", "CLOSEST_DEFENDER", "PERIOD", "PTS", "GAME_CLOCK", "CLOSEST_DEFENDER_PLAYER_ID",
                                  "player_name", "SHOT_RESULT", "MATCHUP"], inplace = True)

    #import pdb; pdb.set_trace()


    pandas_matrix.to_csv("new.csv") #write to new csv file so we don't have to deal with the long run time of this script!


if __name__ == "__main__":
    main()


