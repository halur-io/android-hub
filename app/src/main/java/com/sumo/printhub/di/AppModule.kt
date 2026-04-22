package com.sumo.printhub.di

import android.content.Context
import com.sumo.printhub.data.api.PrintHubApi
import com.sumo.printhub.data.api.SseClient
import com.sumo.printhub.data.local.ConfigCache
import com.sumo.printhub.data.local.SecurePrefs
import com.sumo.printhub.data.repository.PrintHubRepository
import com.sumo.printhub.print.TcpRelay
import dagger.Module
import dagger.Provides
import dagger.hilt.InstallIn
import dagger.hilt.android.qualifiers.ApplicationContext
import dagger.hilt.components.SingletonComponent
import kotlinx.serialization.json.Json
import okhttp3.OkHttpClient
import okhttp3.logging.HttpLoggingInterceptor
import java.util.concurrent.TimeUnit
import javax.inject.Singleton

@Module
@InstallIn(SingletonComponent::class)
object AppModule {

    @Provides @Singleton
    fun provideJson(): Json = Json {
        ignoreUnknownKeys = true
        coerceInputValues = true
        encodeDefaults = true
    }

    @Provides @Singleton
    fun provideOkHttp(): OkHttpClient {
        val log = HttpLoggingInterceptor().apply {
            level = HttpLoggingInterceptor.Level.BASIC
        }
        return OkHttpClient.Builder()
            .connectTimeout(15, TimeUnit.SECONDS)
            .readTimeout(60, TimeUnit.SECONDS)
            .writeTimeout(15, TimeUnit.SECONDS)
            .retryOnConnectionFailure(true)
            .addInterceptor(log)
            .build()
    }

    @Provides @Singleton
    fun provideSseHttp(): OkHttpClient {
        return OkHttpClient.Builder()
            .connectTimeout(15, TimeUnit.SECONDS)
            .readTimeout(0, TimeUnit.MILLISECONDS)
            .pingInterval(30, TimeUnit.SECONDS)
            .retryOnConnectionFailure(true)
            .build()
    }

    @Provides @Singleton
    fun provideSecurePrefs(@ApplicationContext ctx: Context): SecurePrefs =
        SecurePrefs(ctx)

    @Provides @Singleton
    fun provideConfigCache(@ApplicationContext ctx: Context, json: Json): ConfigCache =
        ConfigCache(ctx, json)

    @Provides @Singleton
    fun provideApi(http: OkHttpClient, json: Json, prefs: SecurePrefs): PrintHubApi =
        PrintHubApi(http, json, prefs)

    @Provides @Singleton
    fun provideSseClient(prefs: SecurePrefs, json: Json): SseClient =
        SseClient(provideSseHttp(), prefs, json)

    @Provides @Singleton
    fun provideTcpRelay(): TcpRelay = TcpRelay()

    @Provides @Singleton
    fun provideRepository(
        api: PrintHubApi,
        sse: SseClient,
        prefs: SecurePrefs,
        cache: ConfigCache,
        relay: TcpRelay
    ): PrintHubRepository =
        PrintHubRepository(api, sse, prefs, cache, relay)
}
