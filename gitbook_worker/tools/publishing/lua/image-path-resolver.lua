-- image-path-resolver.lua
-- This filter ensures proper resolution of image paths from .gitbook/assets.

local has_pdf_assets = os.getenv("GITBOOK_SVG_PDF_AVAILABLE") == "1"

local function resolve_image(img)
    local src = img.src or ""

    -- Normalize any relative reference that eventually targets .gitbook/assets
    -- so Pandoc can pick it up from the copied asset directory.
    if not src:match("^https?://") and not src:match("^/") then
        local normalized = src:match("%.gitbook/assets/.*")
        if normalized then
            if has_pdf_assets and normalized:match("%.svg$") then
                img.src = normalized:gsub("%.svg$", ".pdf")
            else
                img.src = normalized
            end
        end
    end

    return img
end

return {
    {
        Image = resolve_image
    }
}