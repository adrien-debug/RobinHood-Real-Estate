#!/usr/bin/env python3
"""
Test des vraies APIs - Script pour vérifier la connectivité
"""
import asyncio
import httpx
from loguru import logger
from core.config import settings


async def test_api_connectivity():
    """Test la connectivité de toutes les APIs"""

    apis_to_test = [
        {
            'name': 'DLD Transactions',
            'url': f"{settings.dld_api_base_url}/transactions",
            'key': settings.dld_api_key,
            'auth_type': 'oauth'
        },
        {
            'name': 'Bayut API',
            'url': f"{settings.bayut_api_url}/properties",
            'key': settings.bayut_api_key,
            'auth_type': 'bearer'
        },
        {
            'name': 'Makani Geocoding',
            'url': f"{settings.makani_api_url}/search",
            'key': settings.makani_api_key,
            'auth_type': 'bearer'
        },
        {
            'name': 'DDA Planning',
            'url': f"{settings.dda_api_url}/building-permits",
            'key': settings.dda_api_key,
            'auth_type': 'bearer'
        }
    ]

    results = {}

    async with httpx.AsyncClient(timeout=10.0) as client:
        for api in apis_to_test:
            api_name = api['name']
            logger.info(f"Testing {api_name}...")

            try:
                headers = {}
                if api['key']:
                    if api['auth_type'] == 'bearer':
                        headers['Authorization'] = f"Bearer {api['key']}"
                    elif api['auth_type'] == 'oauth':
                        # Pour DLD, on utilise client_credentials flow
                        headers['X-API-Key'] = api['key']

                # Test simple GET request
                response = await client.get(api['url'], headers=headers)

                if response.status_code == 200:
                    results[api_name] = {
                        'status': 'SUCCESS',
                        'response_time': response.elapsed.total_seconds(),
                        'message': f"API repond correctement ({response.status_code})"
                    }
                    logger.success(f"✅ {api_name}: API fonctionnelle")
                else:
                    results[api_name] = {
                        'status': 'AUTH_ERROR',
                        'response_time': response.elapsed.total_seconds(),
                        'message': f"Erreur d'authentification ({response.status_code})"
                    }
                    logger.warning(f"⚠️  {api_name}: Probleme d'authentification")

            except httpx.TimeoutException:
                results[api_name] = {
                    'status': 'TIMEOUT',
                    'message': "Timeout - API non accessible"
                }
                logger.error(f"❌ {api_name}: Timeout")

            except httpx.HTTPError as e:
                results[api_name] = {
                    'status': 'HTTP_ERROR',
                    'message': f"Erreur HTTP: {str(e)}"
                }
                logger.error(f"❌ {api_name}: Erreur HTTP")

            except Exception as e:
                results[api_name] = {
                    'status': 'ERROR',
                    'message': f"Erreur generale: {str(e)}"
                }
                logger.error(f"❌ {api_name}: Erreur generale")

    return results


def main():
    """Fonction principale"""
    logger.info("Test de connectivite des APIs Dubai Real Estate")
    logger.info("=" * 50)

    # Test synchrone pour simplifier
    import nest_asyncio
    nest_asyncio.apply()

    results = asyncio.run(test_api_connectivity())

    logger.info("\nResultats finaux:")
    logger.info("-" * 30)

    for api_name, result in results.items():
        status = result['status']
        message = result['message']

        if status == 'SUCCESS':
            logger.success(f"{api_name}: {message}")
        elif status == 'AUTH_ERROR':
            logger.warning(f"{api_name}: {message}")
        else:
            logger.error(f"{api_name}: {message}")

    # Resume
    successful = sum(1 for r in results.values() if r['status'] == 'SUCCESS')
    total = len(results)

    logger.info(f"\nResume: {successful}/{total} APIs fonctionnelles")

    if successful == total:
        logger.success("Toutes les APIs sont operationnelles!")
        return True
    elif successful > 0:
        logger.warning("Certaines APIs fonctionnent, d'autres non")
        return True
    else:
        logger.error("Aucune API ne fonctionne - utilisation du mode mock")
        return False


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)