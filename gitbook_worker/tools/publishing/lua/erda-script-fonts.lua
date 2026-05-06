-- Route scripts covered by dedicated ERDA fallback fonts through explicit
-- LaTeX font macros. This keeps the global fallback chain stable while making
-- visual inspection samples exercise the intended configured fonts.

local function has_codepoint_in_range(text, start_cp, end_cp)
  for _, cp in utf8.codes(text) do
    if cp >= start_cp and cp <= end_cp then
      return true
    end
  end
  return false
end

local function wrap_with_macro(macro, elem)
  return {
    pandoc.RawInline('latex', '\\' .. macro .. '{'),
    elem,
    pandoc.RawInline('latex', '}')
  }
end

function Str(elem)
  if not FORMAT:match('latex') then
    return nil
  end

  if has_codepoint_in_range(elem.text, 0x0900, 0x097F) then
    return wrap_with_macro('erdaIndic', elem)
  end

  if has_codepoint_in_range(elem.text, 0x1200, 0x137F) then
    return wrap_with_macro('erdaEthiopic', elem)
  end

  return nil
end