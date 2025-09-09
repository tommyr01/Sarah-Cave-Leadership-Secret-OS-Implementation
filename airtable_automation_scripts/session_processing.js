// Session Processing Airtable Automation Script
// Triggers when a coaching session record is updated with raw notes
// Sends data to Vercel API for AI processing

let params = input.config();

// Build the webhook payload matching expected format
const payload = {
    webhook: {
        id: 'airtable-automation-' + Date.now(),
        source: 'airtable_automations',
        timestamp: new Date().toISOString()
    },
    base: { 
        id: 'appovmJ15ALIjbpDp' 
    },
    timestamp: new Date().toISOString(),
    changedTablesById: {
        "tblSessions": {
            name: "Coaching Sessions",
            changedRecordsById: {
                [params.recordId]: {
                    current: {
                        fields: {
                            "Client Name": params.clientName || "",
                            "Session Date": params.sessionDate || "",
                            "Session Type": params.sessionType || "Leadership Coaching", 
                            "Duration (minutes)": params.duration || 60,
                            "Raw Notes": params.rawNotes || "",
                            "Session Objectives": params.sessionObjectives || "",
                            "Client Context": params.clientContext || "",
                            "Previous Action Items": params.previousActionItems || "",
                            "Coaching Focus Areas": params.coachingFocusAreas || []
                        }
                    }
                }
            }
        }
    },
    automationType: "session_processing"
};

try {
    // Make the request to Vercel API
    const response = await fetch('https://sarah-cave-leadership-secret-os-imp-three.vercel.app/api/session_processing', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'User-Agent': 'Airtable-Automation/1.0'
        },
        body: JSON.stringify(payload)
    });
    
    console.log('Response Status:', response.status);
    console.log('Response Headers:', JSON.stringify([...response.headers.entries()]));
    
    // Get response text first to debug
    const responseText = await response.text();
    console.log('Raw Response:', responseText);
    
    // Try to parse as JSON
    let responseData;
    try {
        responseData = JSON.parse(responseText);
    } catch (parseError) {
        console.log('❌ JSON Parse Error:', parseError.message);
        console.log('❌ Raw response was:', responseText);
        return;
    }
    
    if (response.ok) {
        console.log('✅ Success:', JSON.stringify(responseData, null, 2));
        console.log('📊 Processed Sessions:', responseData.processed_sessions || 0);
        
        if (responseData.results && responseData.results.length > 0) {
            console.log('📝 First Result:', JSON.stringify(responseData.results[0], null, 2));
        }
    } else {
        console.log('❌ Error Response:', JSON.stringify(responseData, null, 2));
        console.log('❌ Status:', response.status, response.statusText);
    }
    
} catch (error) {
    console.log('❌ Fetch Error:', error.message);
    console.log('❌ Error Type:', error.name);
    console.log('❌ Full Error:', JSON.stringify(error, Object.getOwnPropertyNames(error)));
}