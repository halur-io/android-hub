package com.sumo.printhub.data.api

import com.sumo.printhub.data.local.SecurePrefs
import com.sumo.printhub.data.model.SseEvent
import kotlinx.coroutines.channels.awaitClose
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.callbackFlow
import kotlinx.serialization.json.Json
import okhttp3.OkHttpClient
import okhttp3.Request
import okhttp3.sse.EventSource
import okhttp3.sse.EventSourceListener
import okhttp3.sse.EventSources
import javax.inject.Inject
import javax.inject.Singleton

sealed interface SseStreamEvent {
    data object Open : SseStreamEvent
    data class Message(val event: SseEvent) : SseStreamEvent
    data class Failure(val throwable: Throwable?, val code: Int?) : SseStreamEvent
    data object Closed : SseStreamEvent
}

/**
 * Wraps OkHttp's SSE engine in a coroutine Flow. Reconnect/backoff is handled
 * by the caller (PrintHubRepository) so it can use the configured delay.
 */
@Singleton
class SseClient @Inject constructor(
    private val sseHttp: OkHttpClient,
    private val prefs: SecurePrefs,
    private val json: Json
) {
    fun stream(branchId: Int): Flow<SseStreamEvent> = callbackFlow {
        val factory = EventSources.createFactory(sseHttp)
        val url = "${prefs.getServerUrl()}/ops/api/orders/stream?key=${prefs.getApiKey()}&branch_id=$branchId"

        val req = Request.Builder()
            .url(url)
            .header("Accept", "text/event-stream")
            .header("Cache-Control", "no-cache")
            .build()

        val source: EventSource = factory.newEventSource(req, object : EventSourceListener() {
            override fun onOpen(eventSource: EventSource, response: okhttp3.Response) {
                trySend(SseStreamEvent.Open)
            }

            override fun onEvent(
                eventSource: EventSource,
                id: String?,
                type: String?,
                data: String
            ) {
                runCatching {
                    val parsed = json.decodeFromString(SseEvent.serializer(), data)
                    trySend(SseStreamEvent.Message(parsed))
                }
            }

            override fun onClosed(eventSource: EventSource) {
                trySend(SseStreamEvent.Closed)
            }

            override fun onFailure(
                eventSource: EventSource,
                t: Throwable?,
                response: okhttp3.Response?
            ) {
                trySend(SseStreamEvent.Failure(t, response?.code))
            }
        })

        awaitClose { source.cancel() }
    }
}
