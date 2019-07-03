'''Plugin-level constants.'''


BASE_URL = 'https://leetcode.com/'

LOGIN_URL = 'https://leetcode.com/accounts/login/'

GRAPHQL_URL = 'https://leetcode.com/graphql'

PROBLEM_LIST_URL = 'https://leetcode.com/api/problems/all'

PROBLEM_DESCRIPTION_URL = 'https://leetcode.com/problems/{slug}/description'

SUBMISSION_REFERER_URL = 'https://leetcode.com/problems/{slug}/submissions/'

TEST_URL = 'https://leetcode.com/problems/{slug}/interpret_solution/'

SUBMIT_URL = 'https://leetcode.com/problems/{slug}/submit/'

SUBMISSION_URL = 'https://leetcode.com/submissions/detail/{submission}/'

CHECK_URL = 'https://leetcode.com/submissions/detail/{submission}/check/'

PROBLEM_SET_URL = 'https://leetcode.com/problemset/all/'

GET_PROBLEM_QUERY = '''
query questionData($titleSlug: String!) {
  question(titleSlug: $titleSlug) {
    questionId
    questionFrontendId
    boundTopicId
    title
    titleSlug
    content
    isPaidOnly
    difficulty
    likes
    dislikes
    isLiked
    similarQuestions
    contributors {
      username
      profileUrl
      avatarUrl
      __typename
    }
    langToValidPlayground
    topicTags {
      name
      slug
      translatedName
      __typename
    }
    companyTagStats
    codeSnippets {
      lang
      langSlug
      code
      __typename
    }
    stats
    hints
    solution {
      id
      canSeeDetail
      __typename
    }
    status
    sampleTestCase
    metaData
    judgerAvailable
    judgeType
    mysqlSchemas
    enableRunCode
    enableTestMode
    envInfo
    libraryUrl
    __typename
  }
}
'''.strip()

GET_SUBMISSION_LIST_QUERY = '''
query Submissions($offset: Int!, $limit: Int!, $lastKey: String, $questionSlug: String!) {
  submissionList(offset: $offset, limit: $limit, lastKey: $lastKey, questionSlug: $questionSlug) {
    lastKey
    hasNext
    submissions {
      id
      statusDisplay
      lang
      runtime
      timestamp
      url
      isPending
      memory
      __typename
    }
    __typename
  }
}
'''
