using Telegram.Bot.Polling;
using TelegramBot;
using TelegramBot.Services;
using TelegramBot.Services.Handlers;
using TelegramBot.Services.Rag;

var builder = WebApplication.CreateBuilder(args);

// Add services to the container.
// Learn more about configuring OpenAPI at https://aka.ms/aspnet/openapi
builder.Services.AddOpenApi();

var config = builder.Configuration.GetSection("Bot").Get<Config>()
             ?? throw new InvalidOperationException("Section 'Bot' is missing in configuration");
builder.Services.AddSingleton(config);

builder.Services.AddHttpClient<RagClient>(c =>
{
    c.BaseAddress = new Uri(config.RagUrlBase);
    c.Timeout = TimeSpan.FromMinutes(5);
});
builder.Services.AddSingleton<IUpdateHandler, BotHandler>();
builder.Services.AddHostedService<TgBotPollingService>();

var app = builder.Build();

// Configure the HTTP request pipeline.
if (app.Environment.IsDevelopment())
{
    app.MapOpenApi();
}

app.UseHttpsRedirection();

var summaries = new[]
{
    "Freezing", "Bracing", "Chilly", "Cool", "Mild", "Warm", "Balmy", "Hot", "Sweltering", "Scorching"
};

app.MapGet("/weatherforecast", () =>
    {
        var forecast = Enumerable.Range(1, 5).Select(index =>
                new WeatherForecast
                (
                    DateOnly.FromDateTime(DateTime.Now.AddDays(index)),
                    Random.Shared.Next(-20, 55),
                    summaries[Random.Shared.Next(summaries.Length)]
                ))
            .ToArray();
        return forecast;
    })
    .WithName("GetWeatherForecast");

app.Run();

record WeatherForecast(DateOnly Date, int TemperatureC, string? Summary)
{
    public int TemperatureF => 32 + (int)(TemperatureC / 0.5556);
}