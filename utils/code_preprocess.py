def truncate_code(s):
    first = s.find('```')
    if first != -1:
        second = s.find('```', first + 3)
        if second != -1:
            return s[first + 3:second]
    else:
      first = s.find('import turtle')
      return s[first:]


def preprocess_response(response):
  truncated = truncate_code(response)
  if truncated:
    clean_code = truncated.replace('`', '').replace('python', '', 1).\
      replace('Python', '', 1).replace('turtle.done()', '').replace('t.done()', '')\
      .replace('.mainloop()', '').replace('.exitonclick()', '').strip()
  else:
    return None
  return clean_code