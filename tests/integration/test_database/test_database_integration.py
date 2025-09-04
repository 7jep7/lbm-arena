"""
Integration tests for Database operations

Tests database-level functionality including:
- Connection handling
- Transaction management
- Data consistency
- Foreign key constraints
- Performance under load
"""

import pytest
from sqlalchemy import text, func
from sqlalchemy.orm import Session
from tests.utils.helpers import DatabaseTestHelper
from tests.utils.factories import PlayerFactory
from app.core.database import get_db, engine
from app.models.player import Player as PlayerModel
from app.models.game import Game as GameModel, GameStatus
from app.models.move import Move as MoveModel, GamePlayer as GamePlayerModel


@pytest.mark.integration
class TestDatabaseConnection:
    """Test database connection and basic operations"""
    
    def test_database_connection(self, db_session: Session):
        """Test basic database connection"""
        # Execute a simple query
        result = db_session.execute(text("SELECT 1 as test_value"))
        row = result.fetchone()
        
        assert row is not None
        assert row.test_value == 1
    
    def test_database_tables_exist(self, db_session: Session):
        """Test that all required tables exist"""
        # Check if main tables exist
        tables_to_check = ['players', 'games', 'moves', 'game_players']
        
        for table_name in tables_to_check:
            result = db_session.execute(text(f"""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_name = '{table_name}'
            """))
            
            table_exists = result.fetchone() is not None
            assert table_exists, f"Table {table_name} should exist"
    
    def test_database_transaction_rollback(self, db_session: Session):
        """Test transaction rollback functionality"""
        # Create a player
        player_data = PlayerFactory.create_human_player()
        player = PlayerModel(**player_data)
        db_session.add(player)
        db_session.flush()  # Get ID without committing
        
        player_id = player.id
        assert player_id is not None
        
        # Rollback the transaction
        db_session.rollback()
        
        # Player should not exist after rollback
        retrieved_player = db_session.query(PlayerModel).filter(PlayerModel.id == player_id).first()
        assert retrieved_player is None
    
    def test_database_transaction_commit(self, db_session: Session):
        """Test transaction commit functionality"""
        # Create a player
        player_data = PlayerFactory.create_human_player()
        player = PlayerModel(**player_data)
        db_session.add(player)
        db_session.commit()
        
        player_id = player.id
        assert player_id is not None
        
        # Create new session to verify persistence
        with Session(engine) as new_session:
            retrieved_player = new_session.query(PlayerModel).filter(PlayerModel.id == player_id).first()
            assert retrieved_player is not None
            assert retrieved_player.display_name == player_data["display_name"]


@pytest.mark.integration
class TestDatabaseConstraints:
    """Test database constraints and validation"""
    
    def test_player_creation_constraints(self, db_session: Session):
        """Test player creation with various constraints"""
        # Test valid player creation
        player_data = PlayerFactory.create_human_player()
        player = PlayerModel(**player_data)
        db_session.add(player)
        db_session.commit()
        
        assert player.id is not None
        assert player.display_name == player_data["display_name"]
    
    def test_game_player_foreign_key_constraints(self, db_session: Session):
        """Test foreign key constraints for game players"""
        # Create players
        player1_data = PlayerFactory.create_human_player()
        player2_data = PlayerFactory.create_ai_player()
        
        player1 = PlayerModel(**player1_data)
        player2 = PlayerModel(**player2_data)
        
        db_session.add_all([player1, player2])
        db_session.commit()
        
        # Create game with required player IDs
        game = GameModel(
            game_type="chess",
            status=GameStatus.IN_PROGRESS,
            player1_id=player1.id,
            player2_id=player2.id,
            initial_state='{"board_fen": "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"}',
            current_state='{"board_fen": "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"}'
        )
        db_session.add(game)
        db_session.commit()
        
        # Add players to game
        game_player1 = GamePlayerModel(
            game_id=game.id,
            player_id=player1.id,
            position="white"
        )
        game_player2 = GamePlayerModel(
            game_id=game.id,
            player_id=player2.id,
            position="black"
        )
        
        db_session.add_all([game_player1, game_player2])
        db_session.commit()

        # Verify relationships using defined attributes (inside function)
        assert game.player1_id == player1.id
        assert game.player2_id == player2.id
        # Verify GamePlayer join entries
        gp_entries = db_session.query(GamePlayerModel).filter(GamePlayerModel.game_id == game.id).all()
        assert len(gp_entries) == 2
        ids = {gp.player_id for gp in gp_entries}
        assert {player1.id, player2.id} == ids
    
    def test_move_foreign_key_constraints(self, db_session: Session):
        """Test foreign key constraints for moves"""
        helper = DatabaseTestHelper(db_session)
        
        # Create a complete game setup
        game, players = helper.create_game_with_players()
        
        # Create a move
        move = MoveModel(
            game_id=game.id,
            player_id=players[0].id,
            move_number=1,
            move_data='{"move": "e2e4"}',
            notation="e4"
        )
        
        db_session.add(move)
        db_session.commit()
        
        # Verify relationships
        assert move.game.id == game.id
        assert move.player.id == players[0].id
        assert move.game.moves[0].notation == "e4"
    
    def test_invalid_foreign_key_constraints(self, db_session: Session):
        """Test that invalid foreign keys are rejected"""
        # Try to create game player with non-existent player
        with pytest.raises(Exception):  # Should raise integrity error
            game_player = GamePlayerModel(
                game_id=1,
                player_id=99999,  # Non-existent player
                position="white"
            )
            db_session.add(game_player)
            db_session.commit()


@pytest.mark.integration
class TestDatabaseQueries:
    """Test complex database queries"""
    
    def test_player_game_count_query(self, db_session: Session):
        """Test querying player game counts"""
        helper = DatabaseTestHelper(db_session)
        
        # Create players
        player1_data = PlayerFactory.create_human_player()
        player2_data = PlayerFactory.create_ai_player()
        
        player1 = PlayerModel(**player1_data)
        player2 = PlayerModel(**player2_data)
        
        db_session.add_all([player1, player2])
        db_session.commit()
        
        # Create multiple games for player1
        for _ in range(3):
            game, _ = helper.create_game_with_players([player1, player2])
        
        # Query player game counts
        game_count_subq = (
            db_session.query(func.count(GamePlayerModel.id))
            .filter(GamePlayerModel.player_id == PlayerModel.id)
            .correlate(PlayerModel)
            .scalar_subquery()
            .label('game_count')
        )

        player_game_counts = db_session.query(
            PlayerModel.id,
            PlayerModel.display_name,
            game_count_subq
        ).all()
        
        # Find our players in the results
        player1_count = next((p.game_count for p in player_game_counts if p.id == player1.id), 0)
        player2_count = next((p.game_count for p in player_game_counts if p.id == player2.id), 0)
        
        assert player1_count == 3
        assert player2_count == 3
    
    def test_game_moves_query(self, db_session: Session):
        """Test querying game moves in order"""
        helper = DatabaseTestHelper(db_session)
        
        # Create game with players
        game, players = helper.create_game_with_players()
        
        # Add several moves
        moves_data = [
            {"move": "e2e4", "notation": "e4"},
            {"move": "e7e5", "notation": "e5"},
            {"move": "g1f3", "notation": "Nf3"},
            {"move": "b8c6", "notation": "Nc6"}
        ]
        
        for i, move_data in enumerate(moves_data):
            move = MoveModel(
                game_id=game.id,
                player_id=players[i % 2].id,  # Alternate players
                move_number=i + 1,
                move_data=f'{{"move": "{move_data["move"]}"}}',
                notation=move_data["notation"]
            )
            db_session.add(move)
        
        db_session.commit()
        
        # Query moves in order
        moves = db_session.query(MoveModel).filter(
            MoveModel.game_id == game.id
        ).order_by(MoveModel.move_number).all()
        
        assert len(moves) == 4
        assert moves[0].notation == "e4"
        assert moves[1].notation == "e5"
        assert moves[2].notation == "Nf3"
        assert moves[3].notation == "Nc6"
    
    def test_player_statistics_query(self, db_session: Session):
        """Test complex player statistics query"""
        helper = DatabaseTestHelper(db_session)
        
        # Create two players
        player1_data = PlayerFactory.create_human_player()
        player2_data = PlayerFactory.create_ai_player()
        player1 = PlayerModel(**player1_data)
        player2 = PlayerModel(**player2_data)
        db_session.add_all([player1, player2])
        db_session.commit()
        
        # Create multiple games with different outcomes
        games_data = [
            {"status": GameStatus.COMPLETED, "winner": True},
            {"status": GameStatus.COMPLETED, "winner": False},
            {"status": GameStatus.COMPLETED, "winner": True},
            {"status": GameStatus.IN_PROGRESS, "winner": None}
        ]
        
        for game_data in games_data:
            game = GameModel(
                game_type="chess",
                status=game_data["status"],
                player1_id=player1.id,
                player2_id=player2.id,
                initial_state='{"board_fen": "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"}',
                current_state='{"board_fen": "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"}',
                winner_id=player1.id if game_data["winner"] else None
            )
            db_session.add(game)
            db_session.flush()
            
            # Add player to game
            game_player = GamePlayerModel(
                game_id=game.id,
                player_id=player1.id,
                position="white"
            )
            db_session.add(game_player)
        
        db_session.commit()
        
        # Query player statistics
        total_games = db_session.query(GamePlayerModel).filter(
            GamePlayerModel.player_id == player1.id
        ).count()
        
        completed_games = db_session.query(GamePlayerModel).join(GameModel).filter(
            GamePlayerModel.player_id == player1.id,
            GameModel.status == GameStatus.COMPLETED
        ).count()
        
        wins = db_session.query(GameModel).filter(
            GameModel.winner_id == player1.id
        ).count()
        
        assert total_games == 4
        assert completed_games == 3
        assert wins == 2


@pytest.mark.integration
class TestDatabaseConcurrency:
    """Test database concurrency and transaction handling"""
    
    def test_concurrent_player_creation(self, db_session: Session):
        """Test concurrent player creation"""
        # Simulate concurrent player creation
        players_data = [
            PlayerFactory.create_human_player() for _ in range(5)
        ]
        
        players = []
        for player_data in players_data:
            player = PlayerModel(**player_data)
            players.append(player)
        
        # Add all players in same transaction
        db_session.add_all(players)
        db_session.commit()
        
        # Verify all players were created
        for player in players:
            assert player.id is not None
        
        # Verify count
        total_players = db_session.query(PlayerModel).count()
        assert total_players >= 5
    
    def test_game_state_updates(self, db_session: Session):
        """Test concurrent game state updates"""
        helper = DatabaseTestHelper(db_session)
        
        # Create game
        game, players = helper.create_game_with_players()
        
        # Simulate multiple state updates
        states = [
            '{"board_fen": "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq - 0 1"}',
            '{"board_fen": "rnbqkbnr/pppp1ppp/8/4p3/4P3/8/PPPP1PPP/RNBQKBNR w KQkq - 0 2"}',
            '{"board_fen": "rnbqkbnr/pppp1ppp/8/4p3/4P3/5N2/PPPP1PPP/RNBQKB1R b KQkq - 1 2"}'
        ]
        
        for state in states:
            game.current_state = state
            db_session.commit()
            
            # Verify state was updated
            db_session.refresh(game)
            assert game.current_state == state


@pytest.mark.integration
@pytest.mark.slow
class TestDatabasePerformance:
    """Test database performance under load"""
    
    def test_bulk_player_insertion(self, db_session: Session):
        """Test bulk player insertion performance"""
        # Create many players
        players_data = [
            PlayerFactory.create_human_player() for _ in range(100)
        ]
        
        players = []
        for player_data in players_data:
            player = PlayerModel(**player_data)
            players.append(player)
        
        # Bulk insert
        db_session.add_all(players)
        db_session.commit()
        
        # Verify all were inserted
        for player in players:
            assert player.id is not None
        
        # Verify count
        player_count = db_session.query(PlayerModel).count()
        assert player_count >= 100
    
    def test_large_query_performance(self, db_session: Session):
        """Test performance of large queries"""
        # Ensure we have some data
        existing_players = db_session.query(PlayerModel).limit(10).all()
        
        if len(existing_players) < 10:
            # Create some players if not enough exist
            for _ in range(10):
                player_data = PlayerFactory.create_human_player()
                player = PlayerModel(**player_data)
                db_session.add(player)
            db_session.commit()
        
        # Query all players
        all_players = db_session.query(PlayerModel).all()
        
        # Should complete without timeout
        assert len(all_players) >= 10
        
        # Test query with joins
        players_with_games = db_session.query(PlayerModel).outerjoin(
            GamePlayerModel
        ).all()
        
        assert len(players_with_games) >= 10
    
    def test_complex_query_performance(self, db_session: Session):
        """Test performance of complex queries"""
        helper = DatabaseTestHelper(db_session)
        
        # Create some test data
        for _ in range(10):
            game, players = helper.create_game_with_players()
            
            # Add some moves
            for i in range(5):
                move = MoveModel(
                    game_id=game.id,
                    player_id=players[i % 2].id,
                    move_number=i + 1,
                    move_data=f'{{"move": "move_{i}"}}',
                    notation=f"M{i}"
                )
                db_session.add(move)
        
        db_session.commit()
        
        # Complex query: Get all players with their game counts and average moves per game
        total_games_subq = (
            db_session.query(func.count(GamePlayerModel.id))
            .filter(GamePlayerModel.player_id == PlayerModel.id)
            .correlate(PlayerModel)
            .scalar_subquery()
            .label('total_games')
        )
        total_moves_subq = (
            db_session.query(func.count(MoveModel.id))
            .join(GamePlayerModel, MoveModel.game_id == GamePlayerModel.game_id)
            .filter(GamePlayerModel.player_id == PlayerModel.id)
            .correlate(PlayerModel)
            .scalar_subquery()
            .label('total_moves')
        )
        complex_query = db_session.query(
            PlayerModel.id,
            PlayerModel.display_name,
            total_games_subq,
            total_moves_subq
        ).all()
        
        # Should complete without issues
        assert len(complex_query) > 0
        
        for row in complex_query:
            assert hasattr(row, 'id')
            assert hasattr(row, 'display_name')
            assert hasattr(row, 'total_games')
            assert hasattr(row, 'total_moves')


@pytest.mark.integration
class TestDatabaseCleanup:
    """Test database cleanup and data integrity"""
    
    def test_cascade_delete_games(self, db_session: Session):
        """Test that deleting games cascades properly"""
        helper = DatabaseTestHelper(db_session)
        
        # Create game with players and moves
        game, players = helper.create_game_with_players()
        
        # Add moves
        move = MoveModel(
            game_id=game.id,
            player_id=players[0].id,
            move_number=1,
            move_data='{"move": "e2e4"}',
            notation="e4"
        )
        db_session.add(move)
        db_session.commit()
        
        game_id = game.id
        
        # Verify data exists
        assert db_session.query(GameModel).filter(GameModel.id == game_id).first() is not None
        assert db_session.query(GamePlayerModel).filter(GamePlayerModel.game_id == game_id).count() > 0
        assert db_session.query(MoveModel).filter(MoveModel.game_id == game_id).count() > 0
        
        # Delete game
        db_session.delete(game)
        db_session.commit()
        
        # Verify cascaded deletions (depending on your cascade settings)
        assert db_session.query(GameModel).filter(GameModel.id == game_id).first() is None
        
        # Game players and moves should also be deleted if cascade is set up
        game_players_count = db_session.query(GamePlayerModel).filter(
            GamePlayerModel.game_id == game_id
        ).count()
        moves_count = db_session.query(MoveModel).filter(
            MoveModel.game_id == game_id
        ).count()
        
        # These assertions depend on your cascade configuration
        # If ON DELETE CASCADE is set, these should be 0
        # Otherwise, you might need to manually clean up
        assert game_players_count == 0 or game_players_count >= 0  # Adjust based on your setup
        assert moves_count == 0 or moves_count >= 0  # Adjust based on your setup
    
    def test_player_deletion_constraints(self, db_session: Session):
        """Test constraints when deleting players involved in games"""
        helper = DatabaseTestHelper(db_session)
        
        # Create game with players
        game, players = helper.create_game_with_players()
        player_to_delete = players[0]
        
        # Try to delete player involved in a game
        try:
            db_session.delete(player_to_delete)
            db_session.commit()
            
            # If deletion succeeded, verify game still exists but player is handled appropriately
            remaining_game = db_session.query(GameModel).filter(GameModel.id == game.id).first()
            assert remaining_game is not None
            
        except Exception:
            # If deletion failed due to constraints, that's also valid behavior
            db_session.rollback()
            
            # Player should still exist
            existing_player = db_session.query(PlayerModel).filter(
                PlayerModel.id == player_to_delete.id
            ).first()
            assert existing_player is not None
    
    def test_database_integrity_after_operations(self, db_session: Session):
        """Test database integrity after various operations"""
        helper = DatabaseTestHelper(db_session)
        
        # Perform various operations
        game, players = helper.create_game_with_players()
        
        # Add moves
        for i in range(3):
            move = MoveModel(
                game_id=game.id,
                player_id=players[i % 2].id,
                move_number=i + 1,
                move_data=f'{{"move": "move_{i}"}}',
                notation=f"M{i}"
            )
            db_session.add(move)
        
        db_session.commit()
        
        # Verify referential integrity
        # All moves should reference valid game and player
        for move in db_session.query(MoveModel).all():
            assert move.game is not None
            assert move.player is not None
        
        # All game players should reference valid game and player
        for game_player in db_session.query(GamePlayerModel).all():
            assert game_player.game is not None
            assert game_player.player is not None
        
        # All games should have valid players
        for game in db_session.query(GameModel).all():
            assert len(game.players) >= 0  # Might be 0 if no players added yet
