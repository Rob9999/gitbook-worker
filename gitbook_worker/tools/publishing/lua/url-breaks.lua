-- Convert visible URL text to LaTeX \url{...} so long references can break.

local function is_latex_output()
  return FORMAT:match('latex') or FORMAT:match('beamer')
end

local function count_char(text, char)
  local _, count = text:gsub('%' .. char, '')
  return count
end

local function strip_trailing_punctuation(text)
  local url = text
  local trailing = ''

  while #url > 0 do
    local last = url:sub(-1)
    local should_strip = last == '.' or last == ',' or last == ';' or last == ':'

    if last == ')' then
      should_strip = count_char(url, '(') < count_char(url, ')')
    elseif last == ']' then
      should_strip = count_char(url, '[') < count_char(url, ']')
    end

    if not should_strip then
      break
    end

    trailing = last .. trailing
    url = url:sub(1, -2)
  end

  return url, trailing
end

local function split_access_suffix(text)
  local lower_text = text:lower()
  local markers = {
    '%(zugriff',
    '%(abgerufen',
    '%(accessed',
    '%(retrieved',
    '%(last%s+accessed',
  }

  local first_marker = nil
  for _, marker in ipairs(markers) do
    local marker_pos = lower_text:find(marker)
    if marker_pos and (first_marker == nil or marker_pos < first_marker) then
      first_marker = marker_pos
    end
  end

  if not first_marker then
    return text, ''
  end

  return text:sub(1, first_marker - 1), text:sub(first_marker)
end

local function looks_like_url(text)
  return text:match('^https?://%S+$') ~= nil
end

local function escape_url_for_latex(url)
  return url:gsub('\\', '\\textbackslash{}'):gsub('{', '\\{'):gsub('}', '\\}')
end

local function raw_url(url)
  return pandoc.RawInline('latex', '\\url{' .. escape_url_for_latex(url) .. '}')
end

local function link_filter(elem)
  if not is_latex_output() then
    return nil
  end

  local target = elem.target or ''
  if not looks_like_url(target) then
    return nil
  end

  local visible_text = pandoc.utils.stringify(elem.content)
  if visible_text == target then
    return raw_url(target)
  end

  return nil
end

local function str_filter(elem)
  if not is_latex_output() then
    return nil
  end

  local text = elem.text
  local result = {}
  local cursor = 1
  local changed = false

  while cursor <= #text do
    local start_pos, end_pos = text:find('https?://%S+', cursor)
    if not start_pos then
      break
    end

    local before = text:sub(cursor, start_pos - 1)
    if before ~= '' then
      table.insert(result, pandoc.Str(before))
    end

    local matched_text = text:sub(start_pos, end_pos)
    local url_candidate, suffix = split_access_suffix(matched_text)
    local url, trailing = strip_trailing_punctuation(url_candidate)
    trailing = trailing .. suffix
    if url == '' or not looks_like_url(url) then
      table.insert(result, pandoc.Str(matched_text))
    else
      table.insert(result, raw_url(url))
      if trailing ~= '' then
        table.insert(result, pandoc.Str(trailing))
      end
      changed = true
    end

    cursor = end_pos + 1
  end

  if not changed then
    return nil
  end

  local after = text:sub(cursor)
  if after ~= '' then
    table.insert(result, pandoc.Str(after))
  end

  return result
end

return {
  { Link = link_filter },
  { Str = str_filter },
}