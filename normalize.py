import pandas as pd
import numpy as np
import multiprocessing
import time
import os


def normalizeData(week):
    prev_time = time.time()
    print(f"Week{week} | Started script | {round(time.time()-prev_time, 4)} s")
    prev_time = time.time()

    track_df = pd.read_csv(f"./bdbdata/week{week}.csv", low_memory=False).drop_duplicates().reset_index(drop=True)
    games_df = pd.read_csv("./bdbdata/games.csv", low_memory=False).reset_index(drop=True)
    plays_df = pd.read_csv("./bdbdata/plays.csv", low_memory=False).reset_index(drop=True)

    print(f"Week{week} | Done reading {len(track_df)} rows | {round(time.time()-prev_time, 4)} s")
    prev_time = time.time()

    track_df['nflId'] = track_df.nflId.fillna(0)  # add an ID to the rows with a football

    track_df = track_df.join(games_df[['gameId', 'homeTeamAbbr', 'visitorTeamAbbr']].set_index('gameId'), on=['gameId'])
    track_df['teamAbbr'] = np.select(
        [track_df.team == 'home', track_df.team == 'away'],
        [track_df.homeTeamAbbr, track_df.visitorTeamAbbr],
        default='FTBL')

    track_df = track_df.join(plays_df[['gameId', 'playId', 'possessionTeam']
                                      ].set_index(['gameId', 'playId']), on=['gameId', 'playId'])
    track_df['team_pos'] = np.select([track_df.teamAbbr == 'FTBL', track_df.teamAbbr ==
                                      track_df.possessionTeam, True], ['FTBL', 'OFF', 'DEF'])

    track_df = track_df.drop(columns=['homeTeamAbbr', 'visitorTeamAbbr', 'possessionTeam'])

    # add los columns
    los = track_df.loc[(track_df.nflId == 0) & (track_df.event == 'ball_snap')][['gameId', 'playId', 'x']
                                                                                ].rename({'x': 'los'}, axis=1).set_index(['gameId', 'playId'])
    track_df = track_df.join(los, on=['gameId', 'playId'])
    track_df['los_norm'] = track_df.los
    track_df.loc[track_df.playDirection == 'left', 'los_norm'] = 120-track_df.los_norm
    track_df.head()

    # add column for which frame the pass play has effectively ended
    play_end_frm = track_df.loc[(track_df.displayName == 'Football') & track_df.event.isin(
        ['pass_forward', 'pass_shovel', 'qb_sack', 'qb_spike', 'qb_strip_sack', 'out_of_bounds']),
        ['gameId', 'playId', 'frameId']].groupby(['gameId', 'playId'],
                                                 as_index=False).first().rename(columns={'frameId': 'play_end_frm'}).set_index(['gameId', 'playId'])
    track_df = track_df.join(play_end_frm, on=['gameId', 'playId'])

    print(f"Week{week} | Done joins | {round(time.time()-prev_time, 4)} s")
    prev_time = time.time()

    track_df['x_norm'] = track_df['x']-(track_df['los']-track_df['los_norm'])
    track_df['y_norm'] = track_df['y']
    track_df['o_norm'] = track_df['o']
    track_df['dir_norm'] = track_df['dir']
    track_df.reset_index(drop=True, inplace=True)
    track_df.loc[track_df.playDirection == 'left', 'x_norm'] = (
        track_df['los_norm']-track_df['x_norm'])+track_df['los_norm']
    track_df.loc[track_df.playDirection == 'left', 'y_norm'] = (53.3/2-track_df['y_norm'])+53.3/2
    track_df.loc[track_df.playDirection == 'left', 'o_norm'] = (track_df['o_norm']+180) % 360
    track_df.loc[track_df.playDirection == 'left', 'dir_norm'] = (track_df['dir_norm']+180) % 360
    track_df = track_df.drop(['x', 'y', 'o', 'dir', 'los', 'playDirection'], axis=1).rename(
        columns={'x_norm': 'x', 'y_norm': 'y', 'o_norm': 'o', 'dir_norm': 'dir', 'los_norm': 'los'})

    track_df['o'] = (-(track_df['o']-90)) % 360
    track_df['dir'] = (-(track_df['dir']-90)) % 360
    track_df['o_rad'] = track_df['o']*np.pi/180
    track_df['dir_rad'] = track_df['dir']*np.pi/180

    deltaT = 0.1
    track_df = track_df.rename(columns={'dir_rad': 'v_old_dir_rad', 'dir': 'v_old_dir', 's': 'v_old'})
    track_df['v_old_x'] = np.cos(track_df.v_old_dir_rad) * track_df.v_old
    track_df['v_old_y'] = np.sin(track_df.v_old_dir_rad) * track_df.v_old

    track_df['v_x'] = track_df.groupby(['gameId', 'playId', 'nflId'])['x'].diff().fillna(0)/deltaT
    track_df['v_y'] = track_df.groupby(['gameId', 'playId', 'nflId'])['y'].diff().fillna(0)/deltaT
    track_df['v'] = np.sqrt(track_df.v_x*track_df.v_x+track_df.v_y*track_df.v_y)
    track_df['v_dir_rad'] = (np.arctan(track_df.v_y/track_df.v_x) % (np.pi*2)).fillna(0)
    track_df['v_dir'] = (track_df['v_dir_rad']*180/np.pi) % 360

    track_df = track_df.rename(columns={'a': 'a_old'})
    track_df['a_x'] = track_df.groupby(['gameId', 'playId', 'nflId'])['v_x'].diff().fillna(0)/deltaT
    track_df['a_y'] = track_df.groupby(['gameId', 'playId', 'nflId'])['v_y'].diff().fillna(0)/deltaT
    track_df['a'] = np.sqrt(track_df.a_x*track_df.a_x+track_df.a_y*track_df.a_y)
    track_df['a_dir_rad'] = (np.arctan(track_df.a_y/track_df.a_x) % (np.pi*2)).fillna(0)
    track_df['a_dir'] = (track_df['a_dir_rad']*180/np.pi) % 360

    mapping = {'DB': 'DB', 'CB': 'DB', 'S': 'S', 'SS': 'S', 'FS': 'S', 'WR': 'WR', 'MLB': 'LB', 'OLB': 'LB',
               'ILB': 'LB', 'LB': 'LB', 'DL': 'DL', 'DT': 'DL', 'DE': 'DL', 'NT': 'DL', 'QB': 'QB', 'RB': 'RB',
               'HB': 'RB', 'TE': 'TE', 'P': 'ST', 'K': 'ST', 'LS': 'ST', 'FB': 'FB'}
    track_df['position_general'] = track_df.position.map(mapping)
    track_df = track_df.round(2)

    # only keep frames between snap (11) and pass fwd
    track_df = track_df.loc[(track_df.frameId >= 11) & (track_df.frameId <= track_df.play_end_frm)]
    # remove footballs from dataset
    track_df = track_df.loc[track_df.nflId != 0]
    track_df.dropna()
    track_df.drop_duplicates().reset_index(drop=True, inplace=True)

    track_df = track_df[['gameId', 'playId', 'frameId', 'event', 'play_end_frm', 'nflId', 'displayName', 'jerseyNumber', 'position',
                         'position_general', 'team', 'team_pos', 'teamAbbr', 'route', 'time', 'los', 'x', 'y', 'dis', 'o', 'v', 'v_x', 'v_y', 'v_dir',
                         'v_dir_rad', 'a', 'a_x', 'a_y', 'a_dir', 'a_dir_rad', 'v_old', 'v_old_x', 'v_old_y', 'v_old_dir', 'v_old_dir_rad', 'a_old']]

    print(f"Week{week} | Done normalizing | {round(time.time()-prev_time,4)} s")
    prev_time = time.time()

    f = f'./thindata/week{week}_mod.csv'
    track_df.to_csv(f, index=False)

    print(f"Week{week} | Done exporting | Took {round(time.time()-prev_time, 4)} s")
    prev_time = time.time()


WEEKS = list(range(1, 18))
# WEEKS = ['toy']
# normalizeData(2)
pool = multiprocessing.Pool(10)
pool.map(normalizeData, WEEKS)
pool.close()
