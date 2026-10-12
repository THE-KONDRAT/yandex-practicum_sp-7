using Telegram.Bot;
using Telegram.Bot.Polling;
using Telegram.Bot.Types;
using Telegram.Bot.Types.Enums;
using TelegramBot.Services.Rag;
using System.Text;

namespace TelegramBot.Services.Handlers;

public class BotHandler(RagClient rag, ILogger<BotHandler> logger) : IUpdateHandler
{
    public async Task HandleUpdateAsync(ITelegramBotClient bot, Update update, CancellationToken ct)
    {
        if (update.Message is not { Text: { } text } msg)
            return; // TODO: голос
        await bot.SendChatAction(msg.Chat, ChatAction.Typing, cancellationToken: ct);

        try
        {
            var response = await rag.AskAsync(text, voice: false, ct);

            var reply = response.Answer;
            var dontKnow = Convert.ToDecimal(response.DistTop1) > 0.45m;
            if (dontKnow)
                reply = "Я не знаю";

            var sb = new StringBuilder(reply);
            if (!dontKnow && response.Sources.Count > 0)
            {
                sb.Append("\n\nSources:");
                foreach (var s in response.Sources.Take(3))
                    sb.Append($"\n\t— {s.Title}");
            }
            await bot.SendMessage(msg.Chat, sb.ToString(), cancellationToken: ct);
        }
        catch (Exception ex)
        {
            logger.LogError(ex, "RAG request failed");
            await bot.SendMessage(msg.Chat, "Ошибка сервиса, попробуйте позже.", cancellationToken: ct);
        }
    }

    public Task HandleErrorAsync(ITelegramBotClient bot, Exception exception,
        HandleErrorSource source, CancellationToken ct)
    {
        logger.LogError(exception, "Telegram polling error ({Source})", source);
        return Task.CompletedTask;
    }
}