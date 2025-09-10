// Client Health Monitoring Airtable Automation Script
// Triggers when client data is updated to assess health and risk factors
// Sends data to Vercel API for health assessment

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
        "tblClients": {
            name: "Clients",
            changedRecordsById: {
                [params.recordId]: {
                    current: {
                        fields: {
                            "Name": params.clientName || "",
                            "Email": params.email || "",
                            "Company": params.company || "",
                            "Title": params.title || "",
                            "Coaching Start Date": params.coachingStartDate || "",
                            "Last Session Date": params.lastSessionDate || "",
                            "Total Sessions": params.totalSessions || 0,
                            "Session Frequency": params.sessionFrequency || "Bi-weekly",
                            "Engagement Level": params.engagementLevel || "Medium",
                            "Payment Status": params.paymentStatus || "Current",
                            "Satisfaction Score": params.satisfactionScore || 0,
                            "Goals Progress": params.goalsProgress || "",
                            "Current Challenges": params.currentChallenges || "",
                            "Communication Preference": params.communicationPreference || "Email",
                            "Notes": params.notes || ""
                        }
                    }
                }
            }
        }
    },
    automationType: "client_health"
};

try {
    // Make the request to Vercel API
    const response = await fetch('https://sarah-cave-leadership-secret-os-imp-three.vercel.app/api/client_health', {
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
        console.log('📊 Assessed Clients:', responseData.assessed_clients || 0);
        
        if (responseData.results && responseData.results.length > 0) {
            const result = responseData.results[0];
            console.log('👤 Client:', result.client_name);
            console.log('💚 Health Score:', result.health_result?.health_score || 'N/A');
            console.log('⚠️ Risk Level:', result.health_result?.risk_level || 'N/A');
            console.log('📋 Recommendations:', result.health_result?.recommendations?.join(', ') || 'None');
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