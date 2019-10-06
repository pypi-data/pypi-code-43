# from eventsourcing.application.sqlalchemy import SQLAlchemyApplication
# from eventsourcing.domain.model.aggregate import AggregateRoot
# # from player import Player
#
#
# db_path = 'sqlite:////tmp/local_db'
#
# application = SQLAlchemyApplication(
#     uri=db_path,
#     persist_event_type=AggregateRoot.Event
# )
#
# player_1 = AggregateRoot.__create__()
#
# print(f"Player ID: {player_1.id}" )
#
# player_1.__save__()
#
# same_p = application.repository[player_1.id]
# print(f"Retrieved ID: {same_p.id}")
# print(f"Retrieved ID: {type(same_p.id)}")
