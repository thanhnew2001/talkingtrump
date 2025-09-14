import Replicate from 'replicate';

export async function onRequestPost(context) {
  const { request, env } = context;
  
  try {
    const { message, chatHistory = [] } = await request.json();
    
    if (!message) {
      return new Response(JSON.stringify({ error: 'Message is required' }), {
        status: 400,
        headers: { 'Content-Type': 'application/json' }
      });
    }

    console.log('📝 Received message:', message);
    console.log('💬 Chat history length:', chatHistory.length);

    // Get recent news for context
    const recentNews = await getRecentNews(env.NEWS_API_KEY);
    
    // Generate Trump's response
    const trumpResponse = await generateTrumpResponse(message, recentNews, chatHistory, env);
    
    // Generate Trump's voice
    const audioUrl = await generateTrumpVoice(trumpResponse, env);
    
    return new Response(JSON.stringify({
      response: trumpResponse,
      audioUrl: audioUrl
    }), {
      headers: { 'Content-Type': 'application/json' }
    });
    
  } catch (error) {
    console.error('❌ Error in trump-response:', error);
    return new Response(JSON.stringify({ 
      error: 'Internal server error',
      details: error.message 
    }), {
      status: 500,
      headers: { 'Content-Type': 'application/json' }
    });
  }
}

async function getRecentNews(apiKey) {
  if (!apiKey) {
    console.log('⚠️ No NEWS_API_KEY provided, skipping news fetch');
    return [];
  }

  try {
    const response = await fetch(`https://newsapi.org/v2/top-headlines?country=us&apiKey=${apiKey}&pageSize=5`);
    const data = await response.json();
    
    if (data.articles) {
      return data.articles.map(article => ({
        title: article.title,
        description: article.description,
        url: article.url
      }));
    }
    
    return [];
  } catch (error) {
    console.error('❌ Error fetching news:', error);
    return [];
  }
}

async function generateTrumpResponse(message, recentNews, chatHistory, env) {
  console.log('🔑 Environment variables:', {
    hasReplicateToken: !!env.REPLICATE_API_TOKEN,
    tokenLength: env.REPLICATE_API_TOKEN ? env.REPLICATE_API_TOKEN.length : 0
  });
  
  const replicate = new Replicate({
    auth: env.REPLICATE_API_TOKEN
  });

  // Format chat history for context
  const chatContext = chatHistory.length > 0 
    ? chatHistory.map(msg => `${msg.sender}: ${msg.message}`).join('\n')
    : 'No previous conversation.';

  // Format recent news for context
  const newsContext = recentNews.length > 0
    ? recentNews.map(article => `${article.title}: ${article.description}`).join('\n')
    : 'No recent news available.';

  const systemPrompt = `You are Donald Trump in a video call. Respond as Trump would in a natural, conversational way.

CHARACTERISTIC TRUMP TRAITS & SPEAKING PATTERNS:
- Always blame the Biden administration for problems
- Claim you're the expert on everything (economy, foreign policy, etc.)
- Use phrases like "Let me tell you something", "Believe me", "Nobody knows more about [topic] than me"
- Reference your past presidency and achievements
- Be confident and assertive, sometimes boastful
- Use simple, direct language that resonates with everyday Americans
- Reference "the fake news" and "the radical left"
- Talk about "making America great again"
- Use superlatives: "tremendous", "incredible", "fantastic", "the best"
- Reference specific numbers and statistics when possible
- Be conversational and engaging, like you're talking to a friend

IMPORTANT: Do NOT add any prefixes like 'Trump:', 'Donald Trump:', or any other speaker labels to your responses.

CONVERSATION HISTORY:
${chatContext}

RECENT NEWS CONTEXT:
${newsContext}

Respond to the user's message as Trump would, keeping it conversational and under 100 words.`;

  try {
    const output = await replicate.run(
      "meta/meta-llama-3.1-8b-instruct",
      {
        input: {
          prompt: `${systemPrompt}\n\nUser: ${message}\n\nTrump:`,
          max_new_tokens: 150,
          temperature: 0.8,
          top_p: 0.9,
          repetition_penalty: 1.1
        }
      }
    );

    let response = Array.isArray(output) ? output.join('') : output;
    
    // Clean up the response
    response = response.trim();
    
    // Remove any "Trump:" prefixes that might have been added
    response = response.replace(/^(Trump|Donald Trump):\s*/i, '').trim();
    
    console.log('🤖 Generated response:', response);
    return response;
    
  } catch (error) {
    console.error('❌ Error generating response:', error);
    return "I'm having trouble thinking right now, but let me tell you something - this country needs strong leadership, and that's exactly what we had before!";
  }
}

async function generateTrumpVoice(responseText, env) {
  console.log('🎤 Generating Trump voice with token:', !!env.REPLICATE_API_TOKEN);
  
  const replicate = new Replicate({
    auth: env.REPLICATE_API_TOKEN
  });

  try {
    const output = await replicate.run(
      "afiaka87/tortoise-tts:e965838de46580210694f81ede74e91f010d34a310e12a8e25e242797181f7ea",
      {
        input: {
          text: responseText,
          voice_a: "custom_voice",
          voice_b: "disabled",
          voice_c: "disabled",
          voice_d: "disabled",
          preset: "fast",
          seed: 0,
          num_autoregressive_samples: 1,
          diffusion_iterations: 30,
          temperature: 0.8,
          length_penalty: 1.0,
          repetition_penalty: 2.0,
          top_p: 0.8,
          max_mel_tokens: 500,
          cvvp_amount: 0.0,
          breathing_room: 0.0,
          custom_voice: "https://736930aa.talkingtrump.pages.dev/trump_voice.wav"
        }
      }
    );

    const audioUrl = Array.isArray(output) ? output[0] : output;
    console.log('🎵 Generated audio URL:', audioUrl);
    return audioUrl;
    
  } catch (error) {
    console.error('❌ Error generating voice:', error);
    return null;
  }
}