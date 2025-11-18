-- Inject span wrappers with class 'emoji' around emoji characters.
-- This enables downstream filters (latex-emoji.lua) to substitute fonts.

local emoji_ranges = {
  {0x1F300, 0x1F5FF},
  {0x1F600, 0x1F64F},
  {0x1F680, 0x1F6FF},
  {0x1F700, 0x1F77F},
  {0x1F780, 0x1F7FF},
  {0x1F800, 0x1F8FF},
  {0x1F900, 0x1F9FF},
  {0x1FA00, 0x1FA6F},
  {0x1FA70, 0x1FAFF},
  {0x1F1E6, 0x1F1FF},
  {0x2300, 0x23FF},
  {0x2600, 0x26FF},
  {0x2700, 0x27BF},
  {0x25A0, 0x25FF},
}

local emoji_singletons = {
  [0x2B50] = true,
  [0x2B06] = true,
  [0x2934] = true,
  [0x2935] = true,
}

local function is_emoji_base(cp)
  if emoji_singletons[cp] then
    return true
  end
  for _, range in ipairs(emoji_ranges) do
    if cp >= range[1] and cp <= range[2] then
      return true
    end
  end
  return false
end

local function is_emoji_modifier(cp)
  if (cp >= 0xFE00 and cp <= 0xFE0F) or cp == 0x200D then
    return true
  end
  if cp >= 0x1F3FB and cp <= 0x1F3FF then
    return true
  end
  if cp >= 0xE0020 and cp <= 0xE007F then
    return true
  end
  return false
end

local function is_emoji_cp(cp)
  return is_emoji_base(cp) or is_emoji_modifier(cp)
end

local function flush_plain(buffer, result)
  if #buffer > 0 then
    table.insert(result, pandoc.Str(table.concat(buffer)))
    for i = #buffer, 1, -1 do
      buffer[i] = nil
    end
  end
end

local function flush_emoji(buffer, result)
  if #buffer > 0 then
    local text = table.concat(buffer)
    table.insert(result, pandoc.Span({ pandoc.Str(text) }, { "emoji" }))
    for i = #buffer, 1, -1 do
      buffer[i] = nil
    end
  end
end

function Str(elem)
  local text = elem.text
  local plain, emoji = {}, {}
  local result = {}

  for _, cp in utf8.codes(text) do
    local char = utf8.char(cp)
    if is_emoji_cp(cp) then
      flush_plain(plain, result)
      table.insert(emoji, char)
    else
      flush_emoji(emoji, result)
      table.insert(plain, char)
    end
  end

  flush_emoji(emoji, result)
  flush_plain(plain, result)

  if #result == 0 then
    return nil
  elseif #result == 1 then
    return result[1]
  end
  return result
end
