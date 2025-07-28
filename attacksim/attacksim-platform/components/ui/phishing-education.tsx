'use client';

import React from 'react';
import { X, AlertTriangle, Shield, Eye, Lock, ExternalLink } from 'lucide-react';
import { Button } from './button';
import { Card, CardContent, CardHeader, CardTitle } from './card';

interface PhishingEducationProps {
  isOpen: boolean;
  onClose: () => void;
  message?: string;
  cloneType?: string;
  detectedFeatures?: string[];
}

export const PhishingEducation: React.FC<PhishingEducationProps> = ({
  isOpen,
  onClose,
  message = "This was a phishing simulation! Never enter your real credentials on suspicious sites.",
  cloneType = "unknown",
  detectedFeatures = []
}) => {
  if (!isOpen) return null;

  const getCloneSpecificTips = (type: string) => {
    switch (type.toLowerCase()) {
      case 'discord':
        return [
          'Discord\'s real URL is discord.com - always check carefully',
          'Look for the Discord logo and proper branding',
          'Real Discord login uses 2FA when enabled',
          'Discord will never ask for passwords via email links'
        ];
      case 'facebook':
        return [
          'Facebook\'s real URL is facebook.com or m.facebook.com',
          'Check for HTTPS and the blue verification badge',
          'Real Facebook uses sophisticated anti-phishing measures',
          'Be wary of login requests from email links'
        ];
      case 'google':
        return [
          'Google\'s real URL is accounts.google.com for login',
          'Look for the Google logo and material design',
          'Google uses advanced security notifications',
          'Enable 2-Step Verification for better security'
        ];
      default:
        return [
          'Always verify the URL before entering credentials',
          'Look for HTTPS and proper certificates',
          'Be suspicious of urgent or threatening messages',
          'When in doubt, navigate to the site directly'
        ];
    }
  };

  const generalTips = [
    'Never enter credentials on suspicious links from emails',
    'Check the URL carefully - look for misspellings or unusual domains',
    'Look for HTTPS (lock icon) and valid certificates',
    'Use password managers to detect fake sites',
    'Enable two-factor authentication when available',
    'Report suspicious emails to your IT security team'
  ];

  const cloneSpecificTips = getCloneSpecificTips(cloneType);

  return (
    <div className="fixed inset-0 bg-black/80 flex items-center justify-center z-50 p-4">
      <Card className="max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        <CardHeader className="pb-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <AlertTriangle className="h-8 w-8 text-red-500" />
              <CardTitle className="text-xl font-bold text-red-600">
                Security Awareness Alert
              </CardTitle>
            </div>
            <Button
              variant="ghost"
              size="icon"
              onClick={onClose}
              className="h-8 w-8"
            >
              <X className="h-4 w-4" />
            </Button>
          </div>
        </CardHeader>

        <CardContent className="space-y-6">
          {/* Main Educational Message */}
          <div className="bg-red-50 border border-red-200 rounded-lg p-4">
            <p className="text-red-800 font-medium text-center">
              {message}
            </p>
          </div>

          {/* What Happened Section */}
          <div className="space-y-3">
            <h3 className="font-semibold text-gray-900 flex items-center">
              <Shield className="h-5 w-5 mr-2 text-blue-500" />
              What Just Happened?
            </h3>
            <p className="text-gray-700">
              You just interacted with a simulated phishing attack designed to test and improve 
              your cybersecurity awareness. This is part of a security training exercise to help 
              you recognize and avoid real phishing attempts.
            </p>
          </div>

          {/* Detection Features */}
          {detectedFeatures.length > 0 && (
            <div className="space-y-3">
              <h3 className="font-semibold text-gray-900 flex items-center">
                <Eye className="h-5 w-5 mr-2 text-orange-500" />
                Red Flags You Could Have Spotted
              </h3>
              <ul className="space-y-2">
                {detectedFeatures.map((feature, index) => (
                  <li key={index} className="flex items-start space-x-2">
                    <div className="w-2 h-2 bg-orange-400 rounded-full mt-2 flex-shrink-0" />
                    <span className="text-gray-700">{feature}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Clone-Specific Tips */}
          <div className="space-y-3">
            <h3 className="font-semibold text-gray-900 flex items-center">
              <Lock className="h-5 w-5 mr-2 text-green-500" />
              How to Spot Fake {cloneType.charAt(0).toUpperCase() + cloneType.slice(1)} Sites
            </h3>
            <ul className="space-y-2">
              {cloneSpecificTips.map((tip, index) => (
                <li key={index} className="flex items-start space-x-2">
                  <div className="w-2 h-2 bg-green-400 rounded-full mt-2 flex-shrink-0" />
                  <span className="text-gray-700">{tip}</span>
                </li>
              ))}
            </ul>
          </div>

          {/* General Security Tips */}
          <div className="space-y-3">
            <h3 className="font-semibold text-gray-900">
              General Security Best Practices
            </h3>
            <ul className="space-y-2">
              {generalTips.map((tip, index) => (
                <li key={index} className="flex items-start space-x-2">
                  <div className="w-2 h-2 bg-blue-400 rounded-full mt-2 flex-shrink-0" />
                  <span className="text-gray-700">{tip}</span>
                </li>
              ))}
            </ul>
          </div>

          {/* Learning Resources */}
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <h4 className="font-medium text-blue-800 mb-2">
              Want to Learn More?
            </h4>
            <p className="text-blue-700 text-sm mb-3">
              Check out these resources to improve your cybersecurity awareness:
            </p>
            <div className="space-y-2">
              <a 
                href="https://www.cyber.gov.au/acsc/small-and-medium-businesses/advice" 
                target="_blank" 
                rel="noopener noreferrer"
                className="inline-flex items-center text-blue-600 hover:text-blue-800 text-sm"
              >
                <ExternalLink className="h-4 w-4 mr-1" />
                Australian Cyber Security Centre
              </a>
            </div>
          </div>

          {/* Action Button */}
          <div className="flex justify-center pt-4">
            <Button onClick={onClose} className="px-8">
              I Understand - Continue Learning
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}; 