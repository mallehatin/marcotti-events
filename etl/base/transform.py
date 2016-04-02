import pandas as pd

from models.common.enums import ConfederationType, ActionType, ModifierType
from models.common.suppliers import MatchEventMap, MatchMap, CompetitionMap, SeasonMap, PlayerMap
from models.common.overview import Countries, Timezones, Competitions, Seasons, Venues
from models.common.personnel import Players, Managers, Referees, Positions
from models.common.match import MatchLineups
from models.common.events import Modifiers
from models.club import Clubs, ClubLeagueMatches, ClubMap
from .workflows import WorkflowBase


class MarcottiTransform(WorkflowBase):
    """
    Transform and validate extracted data.
    """

    @staticmethod
    def seasons(data_frame):
        return data_frame

    def competitions(self, data_frame):
        if 'country' in data_frame.columns:
            lambdafunc = lambda x: pd.Series(self.get_id(Countries, name=x['country']))
            id_frame = data_frame.apply(lambdafunc, axis=1)
            id_frame.columns = ['country_id']
        elif 'confederation' in data_frame.columns:
            lambdafunc = lambda x: pd.Series(ConfederationType.from_string(x['confed']))
            id_frame = data_frame.apply(lambdafunc, axis=1)
            id_frame.columns = ['confederation']
        else:
            print "Cannot insert Competition record: No Country or Confederation data present"
        return data_frame.join(id_frame)

    def clubs(self, data_frame):
        if 'country' in data_frame.columns:
            lambdafunc = lambda x: pd.Series(self.get_id(Countries, name=x['country']))
            id_frame = data_frame.apply(lambdafunc, axis=1)
            id_frame.columns = ['country_id']
        else:
            print "Cannot insert Club record: No Country data present"
        return data_frame.join(id_frame)

    def venues(self, data_frame):
        lambdafunc = lambda x: pd.Series([
            self.get_id(Countries, name=x['country']),
            self.get_id(Timezones, name=x['timezone'])
        ])
        ids_frame = data_frame.apply(lambdafunc, axis=1)
        ids_frame.columns = ['country_id', 'timezone_id']
        return data_frame.join(ids_frame)

    def positions(self, data_frame):
        lambdafunc = lambda x: pd.Series(self.get_id(Positions, name=x['position']))
        id_frame = data_frame.apply(lambdafunc, axis=1)
        id_frame.columns = ['position_id']
        return data_frame.join(id_frame)

    def players(self, data_frame):
        lambdafunc = lambda x: pd.Series([
            self.get_id(Countries, name=x['country']),
            self.get_id(Positions, name=x['position'])
        ])
        ids_frame = data_frame.apply(lambdafunc, axis=1)
        ids_frame.columns = ['country_id', 'position_id']
        return data_frame.join(ids_frame)

    def managers(self, data_frame):
        lambdafunc = lambda x: pd.Series(self.get_id(Countries, name=x['country']))
        id_frame = data_frame.apply(lambdafunc, axis=1)
        id_frame.columns = ['country_id']
        return data_frame.join(id_frame)

    def referees(self, data_frame):
        lambdafunc = lambda x: pd.Series(self.get_id(Countries, name=x['country']))
        id_frame = data_frame.apply(lambdafunc, axis=1)
        id_frame.columns = ['country_id']
        return data_frame.join(id_frame)

    def league_matches(self, data_frame):
        lambdafunc = lambda x: pd.Series([
            self.get_id(Competitions, name=x['competition']),
            self.get_id(Seasons, name=x['season']),
            self.get_id(Venues, name=x['venue']),
            self.get_id(Clubs, name=x['home_team']),
            self.get_id(Clubs, name=x['away_team']),
            self.get_id(Managers, full_name=x['home_manager']),
            self.get_id(Managers, full_name=x['away_manager']),
            self.get_id(Referees, full_name=x['referee'])
        ])
        ids_frame = data_frame.apply(lambdafunc, axis=1)
        ids_frame.columns = ['competition_id', 'season_id', 'venue_id', 'home_team_id', 'away_team_id',
                             'home_manager_id', 'away_manager_id', 'referee_id']
        return data_frame.join(ids_frame)

    def lineups(self, data_frame):
        lambdafunc = lambda x: pd.Series([
            self.get_id(ClubLeagueMatches,
                        competition_id=self.get_id(Competitions, name=x['competition']),
                        season_id=self.get_id(Seasons, name=x['season']),
                        matchday=x['matchday'],
                        home_team_id=self.get_id(Clubs, name=x['home_team']),
                        away_team_id=self.get_id(Clubs, name=x['away_team'])),
            self.get_id(Clubs, name=x['player_team']),
            self.get_id(Players, full_name=x['player_name'])
        ])
        ids_frame = data_frame.apply(lambdafunc, axis=1)
        ids_frame.columns = ['match_id', 'team_id', 'player_id']
        return data_frame.join(ids_frame)


class MarcottiEventTransform(MarcottiTransform):

    def league_matches(self, data_frame):
        lambdafunc = lambda x: pd.Series([
            self.get_id(CompetitionMap, remote_id=x['remote_competition_id'], supplier_id=self.supplier_id),
            self.get_id(SeasonMap, remote_id=x['remote_season_id'], supplier_id=self.supplier_id),
            self.get_id(MatchMap, remote_id=x['remote_match_id'], supplier_id=self.supplier_id),
            self.get_id(ClubMap, remote_id=x['remote_home_team_id'], supplier_id=self.supplier_id),
            self.get_id(ClubMap, remote_id=x['remote_away_team_id'], supplier_id=self.supplier_id),
            self.get_id(Managers, full_name=x['home_manager']),
            self.get_id(Managers, full_name=x['away_manager']),
            self.get_id(Referees, full_name=x['referee'])
        ])
        ids_frame = data_frame.apply(lambdafunc, axis=1)
        ids_frame.columns = ['competition_id', 'season_id', 'match_id', 'home_team_id', 'away_team_id',
                             'home_manager_id', 'away_manager_id', 'referee_id']
        return data_frame.join(ids_frame)

    def lineups(self, data_frame):
        lambdafunc = lambda x: pd.Series([
            self.get_id(MatchMap, remote_id=x['remote_match_id'], supplier_id=self.supplier_id),
            self.get_id(PlayerMap, remote_id=x['remote_player_id'], supplier_id=self.supplier_id),
            self.get_id(ClubMap, remote_id=x['remote_team_id'], supplier_id=self.supplier_id)
        ])
        ids_frame = data_frame.apply(lambdafunc, axis=1)
        ids_frame.columns = ['match_id', 'player_id', 'team_id']
        return data_frame.join(ids_frame)

    def events(self, data_frame):
        lambdafunc = lambda x: pd.Series([
            self.get_id(MatchMap, remote_id=x['remote_match_id'], supplier_id=self.supplier_id),
            self.get_id(ClubMap, remote_id=x['remote_team_id'], supplier_id=self.supplier_id)
        ])
        ids_frame = data_frame.apply(lambdafunc, axis=1)
        ids_frame.columns = ['match_id', 'team_id']
        return data_frame.join(ids_frame)

    def actions(self, data_frame):
        lambdafunc = lambda x: pd.Series([
            self.get_id(MatchEventMap, remote_id=x['remote_event_id'], supplier_id=self.supplier_id),
            self.get_id(MatchLineups,
                        match_id=self.get_id(MatchMap, remote_id=x['remote_match_id'], supplier_id=self.supplier_id),
                        player_id=self.get_id(PlayerMap, remote_id=x['remote_player_id'],
                                              supplier_id=self.supplier_id)),
            ActionType.from_string(x['action_type']),
            self.get_id(Modifiers, type=ModifierType.from_string(x['modifier_type']))
        ])
        ids_frame = data_frame.apply(lambdafunc, axis=1)
        ids_frame.columns = ['match_id', 'lineup_id', 'type', 'modifier_id']
        return data_frame.join(ids_frame)
