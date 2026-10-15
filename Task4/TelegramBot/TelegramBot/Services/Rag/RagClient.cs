namespace TelegramBot.Services.Rag;

public class SourceDto
{
    public string Title { get; set; } = "";
    public string Source { get; set; } = "";
    public int ChunkId { get; set; }
    public float Dist { get; set; }
}

public class AskResponse
{
    public string Answer { get; set; } = "";
    public string InternalQuery { get; set; } = "";
    public string InternalAnswer { get; set; } = "";
    public float DistTop1 { get; set; }
    public List<SourceDto> Sources { get; set; } = [];
    public string? AudioUrl { get; set; }
}

public class RagClient
{
    private readonly HttpClient _http;
    public RagClient(HttpClient http) => _http = http;

    public async Task<AskResponse> AskAsync(string question, bool voice = false, CancellationToken ct = default)
    {
        for (var attempt = 1; ; attempt++)
        {
            try
            {
                return await SendRequestAsync(question,  voice, ct);
            }
            catch (HttpRequestException) when (attempt < 3)
            {
                await Task.Delay(TimeSpan.FromSeconds(5 * attempt), ct);
            }
        }
    }

    private async Task<AskResponse> SendRequestAsync(string question, bool voice = false, CancellationToken ct = default)
    {
        var response = await _http.PostAsJsonAsync("/ask", new { question, voice }, ct);
        response.EnsureSuccessStatusCode();
        var result = await response.Content.ReadFromJsonAsync<AskResponse>(ct);
        return result ?? throw new InvalidOperationException("Empty response from RAG service");
    }
}