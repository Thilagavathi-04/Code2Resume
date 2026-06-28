import tiktoken

_tokenizer_cache = {}


def get_tokenizer(model: str = "cl100k_base"):
    if model not in _tokenizer_cache:
        _tokenizer_cache[model] = tiktoken.get_encoding(model)
    return _tokenizer_cache[model]


def count_tokens(text: str, model: str = "cl100k_base") -> int:
    if not text:
        return 0
    return len(get_tokenizer(model).encode(text))


def truncate_to_tokens(text: str, max_tokens: int, model: str = "cl100k_base") -> str:
    if not text:
        return ""
    tokenizer = get_tokenizer(model)
    tokens = tokenizer.encode(text)
    if len(tokens) <= max_tokens:
        return text
    return tokenizer.decode(tokens[:max_tokens])


def truncate_at_sentence_boundary(text: str, max_tokens: int, model: str = "cl100k_base") -> str:
    if not text:
        return ""
    tokenizer = get_tokenizer(model)
    tokens = tokenizer.encode(text)
    if len(tokens) <= max_tokens:
        return text
    truncated = tokenizer.decode(tokens[:max_tokens])
    last_period = max(truncated.rfind('.'), truncated.rfind('!'), truncated.rfind('?'))
    if last_period > len(truncated) * 0.7:
        return truncated[:last_period + 1]
    return truncated
