-- Route scripts covered by dedicated ERDA fallback fonts through explicit
-- LaTeX font macros. This keeps the global fallback chain stable while making
-- visual inspection samples exercise the intended configured fonts.

local function has_codepoint_in_range(text, ranges)
  for _, cp in utf8.codes(text) do
    for _, range in ipairs(ranges) do
      if cp >= range[1] and cp <= range[2] then
        return true
      end
    end
  end
  return false
end

local function codepoint_in_ranges(cp, ranges)
  for _, range in ipairs(ranges) do
    if cp >= range[1] and cp <= range[2] then
      return true
    end
  end
  return false
end

local function wrap_text_with_macro(macro, text)
  return {
    pandoc.RawInline('latex', '\\' .. macro .. '{'),
    pandoc.Str(text),
    pandoc.RawInline('latex', '}')
  }
end

local function split_script_runs(text, macro, ranges)
  local result = {}
  local buffer = {}
  local buffer_is_script = nil

  local function flush()
    if #buffer == 0 then
      return
    end
    local segment = table.concat(buffer)
    if buffer_is_script then
      for _, inline in ipairs(wrap_text_with_macro(macro, segment)) do
        table.insert(result, inline)
      end
    else
      table.insert(result, pandoc.Str(segment))
    end
    buffer = {}
  end

  for _, cp in utf8.codes(text) do
    local char = utf8.char(cp)
    local is_script = codepoint_in_ranges(cp, ranges)
    if buffer_is_script ~= nil and is_script ~= buffer_is_script then
      flush()
    end
    buffer_is_script = is_script
    table.insert(buffer, char)
  end
  flush()

  if #result == 1 and result[1].tag == 'Str' then
    return nil
  end
  return result
end

local INDIC_RANGES = {
  {0x0900, 0x097F},
  {0xA8E0, 0xA8FF}
}

local ETHIOPIC_RANGES = {
  {0x1200, 0x137F},
  {0x1380, 0x139F},
  {0x2D80, 0x2DDF},
  {0xAB00, 0xAB2F},
  {0x1E7E0, 0x1E7FF}
}

function Str(elem)
  if not FORMAT:match('latex') then
    return nil
  end

  if has_codepoint_in_range(elem.text, INDIC_RANGES) then
    return split_script_runs(elem.text, 'erdaIndic', INDIC_RANGES)
  end

  if has_codepoint_in_range(elem.text, ETHIOPIC_RANGES) then
    return split_script_runs(elem.text, 'erdaEthiopic', ETHIOPIC_RANGES)
  end

  return nil
end