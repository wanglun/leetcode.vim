'''The exceptions that may be raised by the leetcode plugin.'''


class LeetCodeFatalError(Exception):
    '''The fatal error that causes the plugin unable to work.'''


class LeetCodeOperationFailureError(Exception):
    '''An operation cannot be performed successfully.'''
