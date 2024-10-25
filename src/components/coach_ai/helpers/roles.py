# Import standard library modules
from typing import List

# Import third-party library modules
from asyncache import cached
from azure.identity.aio import ClientSecretCredential
from cachetools import TTLCache
from msgraph import GraphServiceClient
from msgraph.generated.users.users_request_builder import UsersRequestBuilder

# Import local modules
import settings
from src.components.coach_ai.helpers.logging import log


@cached(cache=TTLCache(maxsize=32, ttl=60 * 10))
async def get_for_user(user_email: str) -> List[str]:
    """
    Implement the logic here, or call a separate function.
    """
    roles = ["public"]  # Generally all users will have the public role.
    override_roles = _get_override_roles(user_email)

    if override_roles:
        roles.extend(override_roles)
        return roles

    groups = await _get_ad_roles(user_email)
    roles.extend(groups)
    return roles


async def _get_user_id_by_email(client: GraphServiceClient, email: str) -> str:
    """Get the Entra user id by email."""
    if not email:
        return None

    query_params = UsersRequestBuilder.UsersRequestBuilderGetQueryParameters(
        filter=f"mail eq '{email}' or userPrincipalName eq '{email}'",
        select=["id", "mail", "userPrincipalName"],
    )
    request_config = UsersRequestBuilder.UsersRequestBuilderGetRequestConfiguration(
        query_parameters=query_params
    )
    users = await client.users.get(request_config)

    if users:
        return users.value[0].id


async def _get_ad_roles(user_email: str) -> List[str]:
    if not user_email:
        return []

    log.info("Getting AD roles", "api-roles")
    if (
        not settings.AD_TENANT_ID
        or not settings.AD_CLIENT_ID
        or not settings.AD_CLIENT_SECRET
    ):
        raise RuntimeError(
            "Microsoft Graph API keys not found. Set them as environment variables."
        )

    credential = ClientSecretCredential(
        settings.AD_TENANT_ID,
        settings.AD_CLIENT_ID,
        settings.AD_CLIENT_SECRET,
    )
    scopes = ["https://graph.microsoft.com/.default"]
    client = GraphServiceClient(credentials=credential, scopes=scopes)

    try:
        user_id = await _get_user_id_by_email(client, user_email)
        response = await client.users.by_user_id(user_id).transitive_member_of.get()
        groups = [group.id for group in response.value]
        return groups
    except Exception as e:
        log.warning(e, "api-roles")
        return []


def _get_override_roles(user_email: str) -> List[str]:
    admins = {
        "ivan@thinkingmachin.es",
        "renzotimothy@thinkingmachin.es",
        "levy@thinkingmachin.es",
        "mikedc@thinkingmachin.es",
        "josh@thinkingmachin.es",
        "levymedina3@gmail.com",
        "elteo@microsoft.com",
        "Diomedes.Kastanis@microsoft.com",
        "kayleamurao@gmail.com",
        "Brett@boostergpt.com",
        "Angelo@boostergpt.com",
        "bretti.neustadt@gmail.com",
        "jaime@boost-gpt.com",
        "angelo@boost-gpt.com",
    }
    admin_domains = {
        "thinkingmachin.es",
    }
    user_domain = user_email.split("@")[1]
    result = []
    if user_email in admins or user_domain in admin_domains:
        result.append("admin")
    return result


def get_for_file(filepath) -> List[str]:
    """
    Implement logic of getting file permissions here.
    If you don't want to implement RBAC, return ["public"].
    """

    if "admin" in filepath:
        return ["a0b5dd18-598d-46d2-9d6d-e2b9dbd460a8"]  # LLM-Admins
    elif "other" in filepath:
        return ["e14d5046-d6e5-4e05-b191-a0f07da9e15d"]  # LLM-SEC
    return ["public"]
