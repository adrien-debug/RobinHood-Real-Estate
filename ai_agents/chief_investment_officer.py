"""
Agent IA - Chief Investment Officer (CIO)
"""
from typing import Dict, List
from datetime import date
from loguru import logger
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from core.config import settings
from core.db import db


class ChiefInvestmentOfficer:
    """
    Agent IA qui agit comme un CIO immobilier
    
    Responsabilités :
    - Analyser les nouvelles transactions
    - Identifier les changements de régime
    - Prioriser les opportunités
    - Générer un brief matinal actionnable
    """
    
    def __init__(self):
        self.llm = ChatOpenAI(
            model=settings.openai_model,
            temperature=0.3,
            api_key=settings.openai_api_key
        )
    
    def generate_daily_brief(self, target_date: date) -> Dict:
        """
        Générer le brief quotidien du CIO
        
        Returns:
            {
                'zones_to_watch': [{zone, reason}, ...],
                'top_opportunities': [{opp_id, reason}, ...],
                'main_risk': str,
                'strategic_recommendation': str,
                'full_brief_text': str
            }
        """
        logger.info(f"Génération du brief CIO pour {target_date}")
        
        # 1. Collecter les données
        market_data = self._collect_market_data(target_date)
        
        # 2. Analyser avec LLM
        analysis = self._analyze_with_llm(market_data, target_date)
        
        # 3. Sauvegarder dans la base
        self._save_brief(analysis, target_date)
        
        logger.info("✅ Brief CIO généré")
        return analysis
    
    def _collect_market_data(self, target_date: date) -> Dict:
        """Collecter les données du marché"""
        data = {}
        
        # Nouvelles transactions
        query_tx = """
        SELECT COUNT(*) as count, 
               AVG(price_per_sqft) as avg_price,
               community
        FROM transactions
        WHERE transaction_date = %s
        GROUP BY community
        ORDER BY count DESC
        LIMIT 10
        """
        data['new_transactions'] = db.execute_query(query_tx, (target_date,))
        
        # Changements de régime
        query_regime = """
        SELECT community, project, regime, confidence_score
        FROM market_regimes
        WHERE regime_date = %s
        ORDER BY confidence_score DESC
        LIMIT 10
        """
        data['regimes'] = db.execute_query(query_regime, (target_date,))
        
        # Top opportunités
        query_opp = """
        SELECT id, community, building, rooms_bucket,
               discount_pct, global_score, recommended_strategy,
               market_regime
        FROM opportunities
        WHERE detection_date = %s
            AND status = 'active'
        ORDER BY global_score DESC
        LIMIT 10
        """
        data['opportunities'] = db.execute_query(query_opp, (target_date,))
        
        # Baselines clés
        query_baseline = """
        SELECT community, rooms_bucket, 
               median_price_per_sqft, momentum, transaction_count
        FROM market_baselines
        WHERE calculation_date = %s
            AND window_days = 30
        ORDER BY transaction_count DESC
        LIMIT 10
        """
        data['baselines'] = db.execute_query(query_baseline, (target_date,))
        
        return data
    
    def _analyze_with_llm(self, market_data: Dict, target_date: date) -> Dict:
        """Analyser les données avec le LLM"""
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", """Tu es un Chief Investment Officer (CIO) spécialisé en immobilier à Dubaï.
            
Ton rôle : analyser le marché quotidiennement et produire un brief ACTIONNABLE.

TON STYLE :
- Professionnel et direct
- Factuel, basé sur les données
- Recommandations claires
- Aucun blabla

FORMAT DU BRIEF :
1. 3 zones à surveiller aujourd'hui (avec raison précise)
2. 3 opportunités prioritaires (avec stratégie recommandée)
3. 1 risque principal du marché
4. 1 recommandation stratégique claire

Sois concis. Maximum 200 mots au total."""),
            ("user", """Date : {date}

NOUVELLES TRANSACTIONS :
{transactions}

RÉGIMES DE MARCHÉ :
{regimes}

TOP OPPORTUNITÉS :
{opportunities}

BASELINES CLÉS :
{baselines}

Génère le brief quotidien au format JSON :
{{
    "zones_to_watch": [{{"zone": "...", "reason": "..."}}, ...],
    "top_opportunities": [{{"opp_id": "...", "reason": "..."}}, ...],
    "main_risk": "...",
    "strategic_recommendation": "...",
    "summary": "..."
}}""")
        ])
        
        # Formater les données
        transactions_str = self._format_transactions(market_data.get('new_transactions', []))
        regimes_str = self._format_regimes(market_data.get('regimes', []))
        opportunities_str = self._format_opportunities(market_data.get('opportunities', []))
        baselines_str = self._format_baselines(market_data.get('baselines', []))
        
        chain = prompt | self.llm
        
        try:
            response = chain.invoke({
                'date': target_date.isoformat(),
                'transactions': transactions_str,
                'regimes': regimes_str,
                'opportunities': opportunities_str,
                'baselines': baselines_str
            })
            
            # Parser la réponse JSON
            import json
            content = response.content
            
            # Extraire le JSON de la réponse
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0]
            elif "```" in content:
                content = content.split("```")[1].split("```")[0]
            
            analysis = json.loads(content.strip())
            
            # Ajouter le texte complet
            analysis['full_brief_text'] = self._format_full_brief(analysis)
            
            return analysis
        
        except Exception as e:
            logger.error(f"Erreur analyse LLM : {e}")
            # Fallback
            return self._generate_fallback_brief(market_data)
    
    def _format_transactions(self, transactions: List[Dict]) -> str:
        """Formater les transactions pour le prompt"""
        if not transactions:
            return "Aucune transaction"
        
        lines = []
        for tx in transactions[:5]:
            lines.append(f"- {tx['community']}: {tx['count']} tx, avg {tx['avg_price']:.0f} AED/sqft")
        return "\n".join(lines)
    
    def _format_regimes(self, regimes: List[Dict]) -> str:
        """Formater les régimes pour le prompt"""
        if not regimes:
            return "Aucun régime"
        
        lines = []
        for r in regimes[:5]:
            lines.append(f"- {r['community']}: {r['regime']} (conf: {r['confidence_score']:.2f})")
        return "\n".join(lines)
    
    def _format_opportunities(self, opportunities: List[Dict]) -> str:
        """Formater les opportunités pour le prompt"""
        if not opportunities:
            return "Aucune opportunité"
        
        lines = []
        for opp in opportunities[:5]:
            lines.append(
                f"- {opp['community']} / {opp['building']}: "
                f"{opp['discount_pct']:.1f}% discount, "
                f"score {opp['global_score']:.0f}, "
                f"stratégie {opp['recommended_strategy']}"
            )
        return "\n".join(lines)
    
    def _format_baselines(self, baselines: List[Dict]) -> str:
        """Formater les baselines pour le prompt"""
        if not baselines:
            return "Aucune baseline"
        
        lines = []
        for b in baselines[:5]:
            momentum_str = f"{b['momentum']*100:+.1f}%" if b.get('momentum') else "N/A"
            lines.append(
                f"- {b['community']} ({b['rooms_bucket']}): "
                f"{b['median_price_per_sqft']:.0f} AED/sqft, "
                f"momentum {momentum_str}, "
                f"{b['transaction_count']} tx"
            )
        return "\n".join(lines)
    
    def _format_full_brief(self, analysis: Dict) -> str:
        """Formater le brief complet en texte"""
        lines = []
        
        lines.append("=== BRIEF QUOTIDIEN CIO ===\n")
        
        lines.append("ZONES À SURVEILLER :")
        for zone in analysis.get('zones_to_watch', []):
            lines.append(f"• {zone['zone']} : {zone['reason']}")
        
        lines.append("\nOPPORTUNITÉS PRIORITAIRES :")
        for opp in analysis.get('top_opportunities', []):
            lines.append(f"• {opp.get('opp_id', 'N/A')} : {opp['reason']}")
        
        lines.append(f"\nRISQUE PRINCIPAL : {analysis.get('main_risk', 'N/A')}")
        lines.append(f"\nRECOMMANDATION : {analysis.get('strategic_recommendation', 'N/A')}")
        
        if analysis.get('summary'):
            lines.append(f"\n{analysis['summary']}")
        
        return "\n".join(lines)
    
    def _generate_fallback_brief(self, market_data: Dict) -> Dict:
        """Brief de secours si LLM échoue"""
        return {
            'zones_to_watch': [
                {'zone': 'Dubai Marina', 'reason': 'Volume élevé de transactions'},
                {'zone': 'Downtown Dubai', 'reason': 'Momentum positif'},
                {'zone': 'Business Bay', 'reason': 'Opportunités détectées'}
            ],
            'top_opportunities': [
                {'opp_id': 'N/A', 'reason': 'Voir dashboard pour détails'}
            ],
            'main_risk': 'Supply future à surveiller',
            'strategic_recommendation': 'Analyser les opportunités FLIP en priorité',
            'full_brief_text': 'Brief de secours - LLM indisponible'
        }
    
    def _save_brief(self, analysis: Dict, target_date: date):
        """Sauvegarder le brief dans la base"""
        import json
        
        query = """
        INSERT INTO daily_briefs (
            brief_date, zones_to_watch, top_opportunities, 
            main_risk, strategic_recommendation, full_brief_text
        )
        VALUES (%s, %s, %s, %s, %s, %s)
        ON CONFLICT (brief_date) 
        DO UPDATE SET
            zones_to_watch = EXCLUDED.zones_to_watch,
            top_opportunities = EXCLUDED.top_opportunities,
            main_risk = EXCLUDED.main_risk,
            strategic_recommendation = EXCLUDED.strategic_recommendation,
            full_brief_text = EXCLUDED.full_brief_text
        """
        
        with db.get_cursor(dict_cursor=False) as cursor:
            cursor.execute(query, (
                target_date,
                json.dumps(analysis.get('zones_to_watch', [])),
                json.dumps(analysis.get('top_opportunities', [])),
                analysis.get('main_risk', ''),
                analysis.get('strategic_recommendation', ''),
                analysis.get('full_brief_text', '')
            ))
