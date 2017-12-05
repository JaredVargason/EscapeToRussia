import twitter
api = twitter.Api(consumer_key='mYfrY0jQi4Duao8LhcftVt5Nr',
                  consumer_secret='qfN1ZOXL1eW4ZVWErLdL5AAChebnRFjiEEDSeWoq0f1i2OMIV2',
                  access_token_key='926853093907673088-QlGNV9Y1gMMwjWwD0Juv0Lg619fyvTu',
                  access_token_secret='ffg82ZOn5G0Tybrj9DoAdKWMyvhMrNkWhegnKZ6vs928d')

statuses = api.GetUserTimeline(25073877)
print([s.text for s in statuses])
print(len(statuses))