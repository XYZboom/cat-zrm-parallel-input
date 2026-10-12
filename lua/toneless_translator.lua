-- 猫师自然码：按 no_tone 开关追加无声调候选。
local M = {}

function M.init(env)
    env.toneless_schema = Schema('zrm_no_tone')
    env.toneless_translator = Component.Translator(
        env.engine,
        env.toneless_schema,
        'translator',
        'script_translator'
    )
end

function M.func(input, segment, env)
    if not env.engine.context:get_option('no_tone') then
        return
    end

    local translation = env.toneless_translator:query(input, segment)
    if not translation then
        return
    end

    for candidate in translation:iter() do
        yield(candidate)
    end
end

function M.fini(env)
    env.toneless_translator = nil
    env.toneless_schema = nil
end

return M
