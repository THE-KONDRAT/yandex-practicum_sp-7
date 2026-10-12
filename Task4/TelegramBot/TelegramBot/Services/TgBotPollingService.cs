using Telegram.Bot;
using Telegram.Bot.Polling;
using Telegram.Bot.Types.Enums;

namespace TelegramBot.Services;

public class TgBotPollingService(IServiceScopeFactory scopeFactory, Config config, ILogger<TgBotPollingService> logger)  : BackgroundService
{

    protected override async Task ExecuteAsync(CancellationToken stoppingToken)
    {
        var receiverOptions = new ReceiverOptions
        {
            AllowedUpdates = [ UpdateType.Message ],
            DropPendingUpdates = false
        };
        
        using var scope = scopeFactory.CreateScope();
        var handler = scope.ServiceProvider.GetRequiredService<IUpdateHandler>();
        var bot = new TelegramBotClient(config.TgBotToken);

        var attempt = 0;
        while (!stoppingToken.IsCancellationRequested)
        {
            try
            {
                await bot.DeleteWebhook(true, stoppingToken);
                await bot.ReceiveAsync(handler, receiverOptions, cancellationToken: stoppingToken);
            }
            catch (OperationCanceledException) when (stoppingToken.IsCancellationRequested)
            {
                break;
            }
            catch (Exception ex)
            {
                attempt++;
                logger.LogError(ex, "Polling cycle failed (attempt {Attempt}), retrying in 15s", attempt);
                try { await Task.Delay(TimeSpan.FromSeconds(15), stoppingToken); }
                catch (OperationCanceledException) { break; }
            }
        }
    }
}