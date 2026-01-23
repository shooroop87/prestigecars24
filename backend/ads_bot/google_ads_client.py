"""
Google Ads API Client for Prestige Cars 24
"""
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Any

from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.errors import GoogleAdsException

import config

logger = logging.getLogger(__name__)


class GoogleAdsManager:
    """Manager for Google Ads API operations"""
    
    def __init__(self):
        self.client = None
        self.customer_id = config.GOOGLE_ADS_CUSTOMER_ID
        self._init_client()
    
    def _init_client(self):
        """Initialize Google Ads client"""
        try:
            credentials = {
                "developer_token": config.GOOGLE_ADS_DEVELOPER_TOKEN,
                "client_id": config.GOOGLE_ADS_CLIENT_ID,
                "client_secret": config.GOOGLE_ADS_CLIENT_SECRET,
                "refresh_token": config.GOOGLE_ADS_REFRESH_TOKEN,
                "login_customer_id": config.GOOGLE_ADS_LOGIN_CUSTOMER_ID,
                "use_proto_plus": True,
            }
            self.client = GoogleAdsClient.load_from_dict(credentials)
            logger.info("Google Ads client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Google Ads client: {e}")
            self.client = None
    
    def get_today_stats(self) -> Optional[Dict[str, Any]]:
        """Get today's campaign statistics"""
        if not self.client:
            return self._get_mock_data()
        
        try:
            ga_service = self.client.get_service("GoogleAdsService")
            
            query = """
                SELECT
                    campaign.name,
                    campaign.status,
                    metrics.impressions,
                    metrics.clicks,
                    metrics.cost_micros,
                    metrics.conversions,
                    metrics.ctr,
                    metrics.average_cpc
                FROM campaign
                WHERE segments.date = TODAY
                AND campaign.name = '{}'
            """.format(config.CAMPAIGN_NAME)
            
            response = ga_service.search_stream(
                customer_id=self.customer_id,
                query=query
            )
            
            stats = {
                "campaign_name": config.CAMPAIGN_NAME,
                "impressions": 0,
                "clicks": 0,
                "cost": 0.0,
                "conversions": 0,
                "ctr": 0.0,
                "avg_cpc": 0.0,
                "status": "UNKNOWN"
            }
            
            for batch in response:
                for row in batch.results:
                    stats["impressions"] += row.metrics.impressions
                    stats["clicks"] += row.metrics.clicks
                    stats["cost"] += row.metrics.cost_micros / 1_000_000
                    stats["conversions"] += row.metrics.conversions
                    stats["status"] = row.campaign.status.name
            
            if stats["impressions"] > 0:
                stats["ctr"] = (stats["clicks"] / stats["impressions"]) * 100
            if stats["clicks"] > 0:
                stats["avg_cpc"] = stats["cost"] / stats["clicks"]
            
            return stats
            
        except GoogleAdsException as e:
            logger.error(f"Google Ads API error: {e}")
            return self._get_mock_data()
        except Exception as e:
            logger.error(f"Error fetching stats: {e}")
            return self._get_mock_data()
    
    def get_ad_group_stats(self) -> List[Dict[str, Any]]:
        """Get statistics by ad group"""
        if not self.client:
            return self._get_mock_ad_groups()
        
        try:
            ga_service = self.client.get_service("GoogleAdsService")
            
            query = """
                SELECT
                    ad_group.name,
                    ad_group.status,
                    metrics.impressions,
                    metrics.clicks,
                    metrics.cost_micros,
                    metrics.ctr
                FROM ad_group
                WHERE segments.date = TODAY
                AND campaign.name = '{}'
                ORDER BY metrics.clicks DESC
                LIMIT 10
            """.format(config.CAMPAIGN_NAME)
            
            response = ga_service.search_stream(
                customer_id=self.customer_id,
                query=query
            )
            
            ad_groups = []
            for batch in response:
                for row in batch.results:
                    ad_groups.append({
                        "name": row.ad_group.name,
                        "status": row.ad_group.status.name,
                        "impressions": row.metrics.impressions,
                        "clicks": row.metrics.clicks,
                        "cost": row.metrics.cost_micros / 1_000_000,
                        "ctr": row.metrics.ctr * 100
                    })
            
            return ad_groups
            
        except Exception as e:
            logger.error(f"Error fetching ad group stats: {e}")
            return self._get_mock_ad_groups()
    
    def get_search_terms(self, min_impressions: int = 10) -> List[Dict[str, Any]]:
        """Get search terms report"""
        if not self.client:
            return []
        
        try:
            ga_service = self.client.get_service("GoogleAdsService")
            
            query = f"""
                SELECT
                    search_term_view.search_term,
                    metrics.impressions,
                    metrics.clicks,
                    metrics.cost_micros,
                    metrics.ctr
                FROM search_term_view
                WHERE segments.date DURING LAST_7_DAYS
                AND campaign.name = '{config.CAMPAIGN_NAME}'
                AND metrics.impressions >= {min_impressions}
                ORDER BY metrics.impressions DESC
                LIMIT 50
            """
            
            response = ga_service.search_stream(
                customer_id=self.customer_id,
                query=query
            )
            
            terms = []
            for batch in response:
                for row in batch.results:
                    terms.append({
                        "term": row.search_term_view.search_term,
                        "impressions": row.metrics.impressions,
                        "clicks": row.metrics.clicks,
                        "cost": row.metrics.cost_micros / 1_000_000,
                        "ctr": row.metrics.ctr * 100
                    })
            
            return terms
            
        except Exception as e:
            logger.error(f"Error fetching search terms: {e}")
            return []
    
    def pause_campaign(self) -> bool:
        """Pause the campaign"""
        if not self.client:
            logger.warning("Client not initialized, cannot pause campaign")
            return False
        
        try:
            campaign_service = self.client.get_service("CampaignService")
            campaign_operation = self.client.get_type("CampaignOperation")
            
            # Get campaign ID first
            campaign_id = self._get_campaign_id()
            if not campaign_id:
                return False
            
            campaign = campaign_operation.update
            campaign.resource_name = campaign_service.campaign_path(
                self.customer_id, campaign_id
            )
            campaign.status = self.client.enums.CampaignStatusEnum.PAUSED
            
            campaign_operation.update_mask.paths.append("status")
            
            campaign_service.mutate_campaigns(
                customer_id=self.customer_id,
                operations=[campaign_operation]
            )
            
            logger.info(f"Campaign {config.CAMPAIGN_NAME} paused successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error pausing campaign: {e}")
            return False
    
    def enable_campaign(self) -> bool:
        """Enable the campaign"""
        if not self.client:
            return False
        
        try:
            campaign_service = self.client.get_service("CampaignService")
            campaign_operation = self.client.get_type("CampaignOperation")
            
            campaign_id = self._get_campaign_id()
            if not campaign_id:
                return False
            
            campaign = campaign_operation.update
            campaign.resource_name = campaign_service.campaign_path(
                self.customer_id, campaign_id
            )
            campaign.status = self.client.enums.CampaignStatusEnum.ENABLED
            
            campaign_operation.update_mask.paths.append("status")
            
            campaign_service.mutate_campaigns(
                customer_id=self.customer_id,
                operations=[campaign_operation]
            )
            
            logger.info(f"Campaign {config.CAMPAIGN_NAME} enabled successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error enabling campaign: {e}")
            return False
    
    def _get_campaign_id(self) -> Optional[str]:
        """Get campaign ID by name"""
        try:
            ga_service = self.client.get_service("GoogleAdsService")
            
            query = f"""
                SELECT campaign.id, campaign.name
                FROM campaign
                WHERE campaign.name = '{config.CAMPAIGN_NAME}'
            """
            
            response = ga_service.search_stream(
                customer_id=self.customer_id,
                query=query
            )
            
            for batch in response:
                for row in batch.results:
                    return str(row.campaign.id)
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting campaign ID: {e}")
            return None
    
    def _get_mock_data(self) -> Dict[str, Any]:
        """Return mock data for testing without API"""
        return {
            "campaign_name": config.CAMPAIGN_NAME,
            "impressions": 1240,
            "clicks": 18,
            "cost": 32.50,
            "conversions": 2,
            "ctr": 1.45,
            "avg_cpc": 1.81,
            "status": "ENABLED (MOCK DATA)"
        }
    
    def _get_mock_ad_groups(self) -> List[Dict[str, Any]]:
        """Return mock ad group data for testing"""
        return [
            {"name": "Mercedes_G63", "clicks": 6, "cost": 10.20, "ctr": 1.8, "impressions": 333, "status": "ENABLED"},
            {"name": "Generic_Luxury", "clicks": 5, "cost": 8.50, "ctr": 1.5, "impressions": 333, "status": "ENABLED"},
            {"name": "Ferrari_Rental", "clicks": 4, "cost": 7.80, "ctr": 1.4, "impressions": 286, "status": "ENABLED"},
            {"name": "Lamborghini_Rental", "clicks": 2, "cost": 4.00, "ctr": 1.1, "impressions": 182, "status": "ENABLED"},
            {"name": "Audi_Rental", "clicks": 1, "cost": 2.00, "ctr": 0.9, "impressions": 111, "status": "ENABLED"},
        ]


# Singleton instance
ads_manager = GoogleAdsManager()
