// Business Intelligence Airtable Automation Script  
// Can be triggered manually or on a schedule to generate business reports
// Sends request to Vercel API for business intelligence analysis

let params = input.config();

// Build the business intelligence payload
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
    report_type: params.reportType || 'general',
    business_data: {
        // In production, these would be calculated from actual Airtable data
        clients_total: params.clientsTotal || 15,
        active_clients: params.activeClients || 12, 
        sessions_this_month: params.sessionsThisMonth || 28,
        revenue_this_month: params.revenueThisMonth || 8400,
        leads_this_month: params.leadsThisMonth || 7,
        deals_active: params.dealsActive || 3,
        conversion_rate: params.conversionRate || 0.23,
        client_satisfaction: params.clientSatisfaction || 4.7,
        session_completion_rate: params.sessionCompletionRate || 0.95
    },
    automationType: "business_intelligence"
};

try {
    // Make the request to Vercel API
    const response = await fetch('https://sarah-cave-leadership-secret-os-imp-three.vercel.app/api/business_intelligence', {
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
        console.log('📊 Report Generated At:', responseData.report_generated_at);
        
        if (responseData.intelligence_result) {
            const result = responseData.intelligence_result;
            console.log('📈 Business Metrics:');
            console.log('  - Active Clients:', result.business_metrics?.active_clients || 'N/A');
            console.log('  - Monthly Revenue:', result.business_metrics?.monthly_revenue || 'N/A');
            console.log('  - Client Satisfaction:', result.business_metrics?.client_satisfaction || 'N/A');
            
            console.log('📋 Executive Summary:', result.executive_summary || 'No summary');
            
            if (result.key_insights && result.key_insights.length > 0) {
                console.log('💡 Key Insights:');
                result.key_insights.forEach((insight, index) => {
                    console.log(`  ${index + 1}. ${insight}`);
                });
            }
            
            if (result.recommendations && result.recommendations.length > 0) {
                console.log('🎯 Recommendations:');
                result.recommendations.forEach((rec, index) => {
                    console.log(`  ${index + 1}. ${rec}`);
                });
            }
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