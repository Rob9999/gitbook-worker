-- Route text-style checklist symbols through the configured sans font.

local TEXT_SYMBOLS = {
  [0x2610] = true, -- ballot box
  [0x2611] = true, -- ballot box with check
  [0x2612] = true, -- ballot box with x
  [0x2713] = true, -- check mark
  [0x2714] = true, -- heavy check mark
  [0x2717] = true, -- ballot x
  [0x2718] = true, -- heavy ballot x
}

local function flush(buffer, result, is_symbol)
  if #buffer == 0 then
    return
  end

  local text = table.concat(buffer)
  if is_symbol then
    table.insert(result, pandoc.RawInline('latex', '\\erdaTextSymbol{'))
    table.insert(result, pandoc.Str(text))
    table.insert(result, pandoc.RawInline('latex', '}'))
  else
    table.insert(result, pandoc.Str(text))
  end

  for index = #buffer, 1, -1 do
    buffer[index] = nil
  end
end

function Str(elem)
  if not FORMAT:match('latex') then
    return nil
  end

  local result = {}
  local buffer = {}
  local buffer_is_symbol = nil

  for _, cp in utf8.codes(elem.text) do
    local is_symbol = TEXT_SYMBOLS[cp] == true
    if buffer_is_symbol ~= nil and is_symbol ~= buffer_is_symbol then
      flush(buffer, result, buffer_is_symbol)
    end
    buffer_is_symbol = is_symbol
    table.insert(buffer, utf8.char(cp))
  end

  flush(buffer, result, buffer_is_symbol)

  if #result == 0 or (#result == 1 and result[1].tag == 'Str') then
    return nil
  end
  return result
end
