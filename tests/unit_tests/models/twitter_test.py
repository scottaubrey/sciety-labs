from pathlib import Path

from sciety_discovery.providers.twitter import (
    TWITTER_API_AUTHORIZATION_FILE_PATH_ENV_VAR,
    get_doi_from_url_or_none,
    get_twitter_user_article_list_provider_or_none,
    iter_twitter_article_list_item_for_user_tweets_response
)


DOI_1 = '10.1101/doi1'

DOI_ORG_URL_PREFIX = 'https://doi.org/'
DOI_ORG_URL_1 = DOI_ORG_URL_PREFIX + DOI_1


class TestGetDoiFromUrlOrNone:
    def test_should_return_none_if_not_url_containing_doi(self):
        assert get_doi_from_url_or_none('https://example.org') is None

    def test_should_ignore_doi_not_starting_with_10_1101(self):
        assert get_doi_from_url_or_none(DOI_ORG_URL_PREFIX + '10.9999/doi1') is None

    def test_should_return_doi_from_doi_org_url(self):
        assert get_doi_from_url_or_none(DOI_ORG_URL_1) == DOI_1

    def test_should_strip_version_from_biorxiv_url(self):
        assert get_doi_from_url_or_none(
            f'https://www.biorxiv.org/content/{DOI_1}v1'
        ) == DOI_1


class TestIterTwitterArticleListItemForUserTweetsResponse:
    def test_return_empty_response_for_empty_timeline(self):
        result = list(iter_twitter_article_list_item_for_user_tweets_response({
            'data': []
        }))
        assert not result

    def test_return_empty_response_for_item_without_entities_timeline(self):
        result = list(iter_twitter_article_list_item_for_user_tweets_response({
            'data': [{}]
        }))
        assert not result

    def test_return_article_list_item_for_expanded_doi_org_url(self):
        result = list(iter_twitter_article_list_item_for_user_tweets_response({
            'data': [{
                'entities': {
                    'urls': [{
                        'expanded_url': DOI_ORG_URL_1
                    }]
                }
            }]
        }))
        assert [item.article_doi for item in result] == [DOI_1]


class TestGetTwitterUserArticleListProviderOrNone:
    def test_should_return_none_if_env_var_is_not_defined(self, env_mock: dict):
        env_mock.clear()
        assert get_twitter_user_article_list_provider_or_none() is None

    def test_should_return_none_if_file_does_not_exist(self, env_mock: dict, tmp_path: Path):
        env_mock[TWITTER_API_AUTHORIZATION_FILE_PATH_ENV_VAR] = str(tmp_path / 'not-found')
        assert get_twitter_user_article_list_provider_or_none() is None

    def test_should_initialize_provider_with_authorization_file(
        self,
        env_mock: dict,
        tmp_path: Path
    ):
        authorization_file = tmp_path / 'authorization.txt'
        authorization_file.write_text('authorization1')
        env_mock[TWITTER_API_AUTHORIZATION_FILE_PATH_ENV_VAR] = str(authorization_file)
        provider = get_twitter_user_article_list_provider_or_none()
        assert provider is not None
        assert provider.twitter_authorization == authorization_file.read_text()