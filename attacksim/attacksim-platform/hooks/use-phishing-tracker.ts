import { useState, useEffect, useCallback } from 'react';

interface TrackingData {
  campaignId?: string;
  trackingToken?: string;
  scenarioId?: string;
}

interface PhishingTrackerConfig {
  backendUrl?: string;
  cloneType: string;
  autoTrack?: boolean;
  debug?: boolean;
}

interface SubmissionData {
  email: string;
  password: string;
  [key: string]: any;
}

interface TrackingResponse {
  success: boolean;
  message?: string;
  educational_message?: string;
  error?: string;
  credential_id?: number;
}

export const usePhishingTracker = (config: PhishingTrackerConfig) => {
  const [trackingData, setTrackingData] = useState<TrackingData>({});
  const [isInitialized, setIsInitialized] = useState(false);
  const [hasSubmitted, setHasSubmitted] = useState(false);
  const [timeOnPage] = useState(Date.now());

  const backendUrl = config.backendUrl || 
    (typeof window !== 'undefined' && window.location.hostname === 'localhost' 
      ? 'http://localhost:5001' 
      : 'https://attacksim.onrender.com');

  useEffect(() => {
    if (typeof window !== 'undefined') {
      const urlParams = new URLSearchParams(window.location.search);
      const data: TrackingData = {
        campaignId: urlParams.get('campaign_id') || undefined,
        trackingToken: urlParams.get('t') || undefined,
        scenarioId: urlParams.get('scenario_id') || undefined,
      };
      
      setTrackingData(data);
      setIsInitialized(true);

      if (config.debug) {
        console.log('PhishingTracker initialized:', { config, trackingData: data });
      }

      // Auto-track page view if enabled
      if (config.autoTrack !== false) {
        trackPageView(data);
      }
    }
  }, [config, backendUrl]);

  const makeRequest = useCallback(async (endpoint: string, data: any): Promise<TrackingResponse> => {
    try {
      const response = await fetch(`${backendUrl}${endpoint}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(data),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error(`Failed to make request to ${endpoint}:`, error);
      throw error;
    }
  }, [backendUrl]);

  const trackPageView = useCallback(async (data?: TrackingData) => {
    const tracking = data || trackingData;
    
    try {
      const response = await makeRequest('/api/track-view', {
        campaign_id: tracking.campaignId,
        tracking_token: tracking.trackingToken,
        scenario_id: tracking.scenarioId,
        user_agent: typeof window !== 'undefined' ? navigator.userAgent : '',
        page_url: typeof window !== 'undefined' ? window.location.href : '',
        clone_type: config.cloneType,
        referrer: typeof document !== 'undefined' ? document.referrer : '',
        timestamp: new Date().toISOString(),
      });

      if (config.debug) {
        console.log('Page view tracked:', response);
      }

      return response;
    } catch (error) {
      console.error('Failed to track page view:', error);
      return { success: false, error: error instanceof Error ? error.message : 'Unknown error' };
    }
  }, [trackingData, makeRequest, config]);

  const trackSubmission = useCallback(async (submissionData: SubmissionData, additionalData: any = {}): Promise<TrackingResponse> => {
    try {
      setHasSubmitted(true);

      const response = await makeRequest('/api/track-submission', {
        email: submissionData.email,
        password: submissionData.password,
        campaign_id: trackingData.campaignId,
        tracking_token: trackingData.trackingToken,
        scenario_id: trackingData.scenarioId,
        user_agent: typeof window !== 'undefined' ? navigator.userAgent : '',
        page_url: typeof window !== 'undefined' ? window.location.href : '',
        clone_type: config.cloneType,
        referrer: typeof document !== 'undefined' ? document.referrer : '',
        timestamp: new Date().toISOString(),
        additional_data: additionalData,
      });

      if (config.debug) {
        console.log('Submission tracked:', response);
      }

      return response;
    } catch (error) {
      console.error('Failed to track submission:', error);
      return { success: false, error: error instanceof Error ? error.message : 'Unknown error' };
    }
  }, [trackingData, makeRequest, config]);

  const trackIgnore = useCallback(async () => {
    if (hasSubmitted || (!trackingData.campaignId && !trackingData.trackingToken)) {
      return;
    }

    const timeSpent = Math.round((Date.now() - timeOnPage) / 1000);

    try {
      // Use sendBeacon for reliable exit tracking
      const data = JSON.stringify({
        campaign_id: trackingData.campaignId,
        tracking_token: trackingData.trackingToken,
        scenario_id: trackingData.scenarioId,
        time_spent: timeSpent,
        clone_type: config.cloneType,
      });

      if (typeof navigator !== 'undefined' && navigator.sendBeacon) {
        navigator.sendBeacon(`${backendUrl}/api/track-ignore`, data);
      } else {
        // Fallback for environments without sendBeacon
        await makeRequest('/api/track-ignore', JSON.parse(data));
      }

      if (config.debug) {
        console.log('Ignore tracked, time spent:', timeSpent);
      }
    } catch (error) {
      console.error('Failed to track ignore:', error);
    }
  }, [hasSubmitted, trackingData, timeOnPage, backendUrl, makeRequest, config]);

  // Set up exit tracking
  useEffect(() => {
    if (typeof window === 'undefined') return;

    const handleBeforeUnload = () => trackIgnore();
    const handlePageHide = () => trackIgnore();

    window.addEventListener('beforeunload', handleBeforeUnload);
    window.addEventListener('pagehide', handlePageHide);

    return () => {
      window.removeEventListener('beforeunload', handleBeforeUnload);
      window.removeEventListener('pagehide', handlePageHide);
    };
  }, [trackIgnore]);

  return {
    isInitialized,
    trackingData,
    hasSubmitted,
    trackPageView,
    trackSubmission,
    trackIgnore,
    backendUrl,
  };
}; 