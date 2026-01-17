"""
🏆 Sports Prediction Bot - Database Module
===========================================

Handles all database operations for tracking predictions, results, and stats.
Supports both SQLite (development) and PostgreSQL (production).
"""

import sqlite3
from datetime import datetime, date, timedelta
from typing import List, Dict, Optional, Any, Tuple
from contextlib import contextmanager
from dataclasses import dataclass, asdict
import json

from src.config import DATABASE_URL, DATA_DIR, logger


# ═══════════════════════════════════════════════════════════════════
# 📊 DATA MODELS
# ═══════════════════════════════════════════════════════════════════

@dataclass
class Prediction:
    """Prediction data model"""
    id: Optional[int] = None
    date: str = ""
    time: str = ""
    league: str = ""
    league_id: str = ""
    home_team: str = ""
    away_team: str = ""
    prediction: str = ""
    prediction_type: str = ""  # 1X2, OVER_UNDER, BTTS, etc.
    odds: float = 0.0
    risk_level: str = ""  # SAFE, VALUE, RISKY
    confidence: int = 0
    post_number: int = 0
    analysis_points: str = ""  # JSON string
    match_id: str = ""
    result: Optional[str] = None  # WIN, LOSS, PUSH, PENDING
    final_score: Optional[str] = None
    is_win: Optional[bool] = None
    profit: Optional[float] = None
    posted_at: Optional[str] = None
    result_updated_at: Optional[str] = None
    fb_post_id: Optional[str] = None


@dataclass
class DailyStats:
    """Daily statistics model"""
    date: str
    total_predictions: int = 0
    wins: int = 0
    losses: int = 0
    pushes: int = 0
    pending: int = 0
    profit: float = 0.0
    hit_rate: float = 0.0


@dataclass
class APIUsage:
    """API usage tracking model"""
    date: str
    count: int = 0
    last_call: Optional[str] = None


# ═══════════════════════════════════════════════════════════════════
# 🗄️ DATABASE CLASS
# ═══════════════════════════════════════════════════════════════════

class Database:
    """
    Database handler for sports prediction tracking.
    Supports SQLite with easy migration path to PostgreSQL.
    """
    
    def __init__(self, db_url: str = DATABASE_URL):
        """Initialize database connection"""
        self.db_url = db_url
        self.db_path = self._parse_db_path()
        self._init_db()
        logger.info(f"📊 Database initialized: {self.db_path}")
    
    def _parse_db_path(self) -> str:
        """Parse database path from URL"""
        if self.db_url.startswith("sqlite:///"):
            return self.db_url.replace("sqlite:///", "")
        return str(DATA_DIR / "predictions.db")
    
    @contextmanager
    def get_connection(self):
        """Context manager for database connections"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            logger.error(f"❌ Database error: {e}")
            raise
        finally:
            conn.close()
    
    def _init_db(self):
        """Initialize database tables"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Predictions table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS predictions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date TEXT NOT NULL,
                    time TEXT NOT NULL,
                    league TEXT NOT NULL,
                    league_id TEXT,
                    home_team TEXT NOT NULL,
                    away_team TEXT NOT NULL,
                    prediction TEXT NOT NULL,
                    prediction_type TEXT,
                    odds REAL NOT NULL,
                    risk_level TEXT NOT NULL,
                    confidence INTEGER NOT NULL,
                    post_number INTEGER NOT NULL,
                    analysis_points TEXT,
                    match_id TEXT,
                    result TEXT DEFAULT 'PENDING',
                    final_score TEXT,
                    is_win INTEGER,
                    profit REAL,
                    posted_at TEXT,
                    result_updated_at TEXT,
                    fb_post_id TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Daily stats table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS daily_stats (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date TEXT UNIQUE NOT NULL,
                    total_predictions INTEGER DEFAULT 0,
                    wins INTEGER DEFAULT 0,
                    losses INTEGER DEFAULT 0,
                    pushes INTEGER DEFAULT 0,
                    pending INTEGER DEFAULT 0,
                    profit REAL DEFAULT 0.0,
                    hit_rate REAL DEFAULT 0.0,
                    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # API usage tracking table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS api_usage (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date TEXT UNIQUE NOT NULL,
                    count INTEGER DEFAULT 0,
                    last_call TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Match cache table (to reduce API calls)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS match_cache (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    match_id TEXT UNIQUE NOT NULL,
                    data TEXT NOT NULL,
                    cached_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    expires_at TEXT NOT NULL
                )
            """)
            
            # Create indexes
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_predictions_date ON predictions(date)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_predictions_match_id ON predictions(match_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_api_usage_date ON api_usage(date)")
            
            logger.debug("✅ Database tables initialized")
    
    # ═══════════════════════════════════════════════════════════════
    # 📝 PREDICTION OPERATIONS
    # ═══════════════════════════════════════════════════════════════
    
    def save_prediction(self, prediction: Prediction) -> int:
        """Save a new prediction to the database"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO predictions (
                    date, time, league, league_id, home_team, away_team,
                    prediction, prediction_type, odds, risk_level, confidence,
                    post_number, analysis_points, match_id, posted_at, fb_post_id
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                prediction.date, prediction.time, prediction.league,
                prediction.league_id, prediction.home_team, prediction.away_team,
                prediction.prediction, prediction.prediction_type, prediction.odds,
                prediction.risk_level, prediction.confidence, prediction.post_number,
                prediction.analysis_points, prediction.match_id,
                prediction.posted_at, prediction.fb_post_id
            ))
            prediction_id = cursor.lastrowid
            logger.info(f"💾 Prediction saved: ID={prediction_id}, {prediction.home_team} vs {prediction.away_team}")
            return prediction_id
    
    def update_result(
        self,
        prediction_id: int,
        result: str,
        final_score: str,
        is_win: bool
    ) -> bool:
        """Update prediction result"""
        profit = self._calculate_profit(prediction_id, is_win)
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE predictions 
                SET result = ?, final_score = ?, is_win = ?, profit = ?,
                    result_updated_at = ?
                WHERE id = ?
            """, (result, final_score, is_win, profit, 
                  datetime.now().isoformat(), prediction_id))
            
            logger.info(f"📊 Result updated: ID={prediction_id}, Result={result}, Win={is_win}")
            return cursor.rowcount > 0
    
    def _calculate_profit(self, prediction_id: int, is_win: bool) -> float:
        """Calculate profit/loss for a prediction (assuming $10 stake)"""
        stake = 10.0
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT odds FROM predictions WHERE id = ?", (prediction_id,))
            row = cursor.fetchone()
            if row:
                odds = row['odds']
                if is_win:
                    return round((odds - 1) * stake, 2)
                return -stake
        return 0.0
    
    def get_prediction_by_id(self, prediction_id: int) -> Optional[Prediction]:
        """Get a single prediction by ID"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM predictions WHERE id = ?", (prediction_id,))
            row = cursor.fetchone()
            if row:
                return self._row_to_prediction(row)
        return None
    
    def get_prediction_by_match_id(self, match_id: str) -> Optional[Prediction]:
        """Get prediction by match ID"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM predictions WHERE match_id = ?", (match_id,))
            row = cursor.fetchone()
            if row:
                return self._row_to_prediction(row)
        return None
    
    def get_daily_predictions(self, target_date: str = None) -> List[Prediction]:
        """Get all predictions for a specific date"""
        if target_date is None:
            target_date = date.today().isoformat()
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM predictions WHERE date = ? ORDER BY post_number",
                (target_date,)
            )
            return [self._row_to_prediction(row) for row in cursor.fetchall()]
    
    def get_pending_predictions(self) -> List[Prediction]:
        """Get all predictions pending results"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM predictions WHERE result = 'PENDING' ORDER BY date, time"
            )
            return [self._row_to_prediction(row) for row in cursor.fetchall()]
    
    def _row_to_prediction(self, row: sqlite3.Row) -> Prediction:
        """Convert database row to Prediction object"""
        return Prediction(
            id=row['id'],
            date=row['date'],
            time=row['time'],
            league=row['league'],
            league_id=row['league_id'],
            home_team=row['home_team'],
            away_team=row['away_team'],
            prediction=row['prediction'],
            prediction_type=row['prediction_type'],
            odds=row['odds'],
            risk_level=row['risk_level'],
            confidence=row['confidence'],
            post_number=row['post_number'],
            analysis_points=row['analysis_points'],
            match_id=row['match_id'],
            result=row['result'],
            final_score=row['final_score'],
            is_win=bool(row['is_win']) if row['is_win'] is not None else None,
            profit=row['profit'],
            posted_at=row['posted_at'],
            result_updated_at=row['result_updated_at'],
            fb_post_id=row['fb_post_id']
        )
    
    # ═══════════════════════════════════════════════════════════════
    # 📊 STATISTICS OPERATIONS
    # ═══════════════════════════════════════════════════════════════
    
    def get_daily_stats(self, target_date: str = None) -> DailyStats:
        """Calculate statistics for a specific date"""
        if target_date is None:
            target_date = date.today().isoformat()
        
        predictions = self.get_daily_predictions(target_date)
        
        wins = sum(1 for p in predictions if p.result == 'WIN')
        losses = sum(1 for p in predictions if p.result == 'LOSS')
        pushes = sum(1 for p in predictions if p.result == 'PUSH')
        pending = sum(1 for p in predictions if p.result == 'PENDING')
        total = len(predictions)
        
        profit = sum(p.profit or 0 for p in predictions)
        hit_rate = (wins / (wins + losses) * 100) if (wins + losses) > 0 else 0
        
        return DailyStats(
            date=target_date,
            total_predictions=total,
            wins=wins,
            losses=losses,
            pushes=pushes,
            pending=pending,
            profit=round(profit, 2),
            hit_rate=round(hit_rate, 1)
        )
    
    def get_weekly_stats(self) -> Dict[str, Any]:
        """Calculate statistics for the current week"""
        today = date.today()
        week_start = today - timedelta(days=today.weekday())
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT 
                    COUNT(*) as total,
                    SUM(CASE WHEN result = 'WIN' THEN 1 ELSE 0 END) as wins,
                    SUM(CASE WHEN result = 'LOSS' THEN 1 ELSE 0 END) as losses,
                    SUM(CASE WHEN result = 'PUSH' THEN 1 ELSE 0 END) as pushes,
                    SUM(CASE WHEN result = 'PENDING' THEN 1 ELSE 0 END) as pending,
                    SUM(COALESCE(profit, 0)) as total_profit
                FROM predictions
                WHERE date >= ?
            """, (week_start.isoformat(),))
            
            row = cursor.fetchone()
            
            wins = row['wins'] or 0
            losses = row['losses'] or 0
            hit_rate = (wins / (wins + losses) * 100) if (wins + losses) > 0 else 0
            
            return {
                'total': row['total'] or 0,
                'wins': wins,
                'losses': losses,
                'pushes': row['pushes'] or 0,
                'pending': row['pending'] or 0,
                'profit': round(row['total_profit'] or 0, 2),
                'hit_rate': round(hit_rate, 1),
                'week_start': week_start.isoformat()
            }
    
    def save_daily_stats(self, stats: DailyStats):
        """Save or update daily statistics"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO daily_stats (date, total_predictions, wins, losses, 
                                         pushes, pending, profit, hit_rate, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(date) DO UPDATE SET
                    total_predictions = excluded.total_predictions,
                    wins = excluded.wins,
                    losses = excluded.losses,
                    pushes = excluded.pushes,
                    pending = excluded.pending,
                    profit = excluded.profit,
                    hit_rate = excluded.hit_rate,
                    updated_at = excluded.updated_at
            """, (
                stats.date, stats.total_predictions, stats.wins, stats.losses,
                stats.pushes, stats.pending, stats.profit, stats.hit_rate,
                datetime.now().isoformat()
            ))
    
    # ═══════════════════════════════════════════════════════════════
    # 📡 API USAGE TRACKING
    # ═══════════════════════════════════════════════════════════════
    
    def get_api_usage_count(self, target_date: str = None) -> int:
        """Get API usage count for a specific date"""
        if target_date is None:
            target_date = date.today().isoformat()
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT count FROM api_usage WHERE date = ?",
                (target_date,)
            )
            row = cursor.fetchone()
            return row['count'] if row else 0
    
    def get_monthly_api_usage(self) -> int:
        """Get total API usage for the current month"""
        today = date.today()
        month_start = today.replace(day=1).isoformat()
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT SUM(count) as total FROM api_usage WHERE date >= ?",
                (month_start,)
            )
            row = cursor.fetchone()
            return row['total'] or 0
    
    def increment_api_usage(self, count: int = 1):
        """Increment API usage counter for today"""
        today = date.today().isoformat()
        now = datetime.now().isoformat()
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO api_usage (date, count, last_call)
                VALUES (?, ?, ?)
                ON CONFLICT(date) DO UPDATE SET
                    count = api_usage.count + excluded.count,
                    last_call = excluded.last_call
            """, (today, count, now))
            
            logger.debug(f"📡 API usage incremented: +{count}")
    
    # ═══════════════════════════════════════════════════════════════
    # 💾 CACHE OPERATIONS
    # ═══════════════════════════════════════════════════════════════
    
    def cache_match_data(self, match_id: str, data: Dict, ttl_hours: int = 6):
        """Cache match data to reduce API calls"""
        expires_at = (datetime.now() + timedelta(hours=ttl_hours)).isoformat()
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO match_cache (match_id, data, cached_at, expires_at)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(match_id) DO UPDATE SET
                    data = excluded.data,
                    cached_at = excluded.cached_at,
                    expires_at = excluded.expires_at
            """, (match_id, json.dumps(data), datetime.now().isoformat(), expires_at))
    
    def get_cached_match(self, match_id: str) -> Optional[Dict]:
        """Get cached match data if still valid"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT data, expires_at FROM match_cache 
                WHERE match_id = ? AND expires_at > ?
            """, (match_id, datetime.now().isoformat()))
            
            row = cursor.fetchone()
            if row:
                return json.loads(row['data'])
        return None
    
    def clear_expired_cache(self):
        """Remove expired cache entries"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "DELETE FROM match_cache WHERE expires_at < ?",
                (datetime.now().isoformat(),)
            )
            deleted = cursor.rowcount
            if deleted > 0:
                logger.debug(f"🗑️ Cleared {deleted} expired cache entries")


# Create singleton instance
db = Database()
