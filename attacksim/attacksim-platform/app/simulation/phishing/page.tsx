import { Shield, AlertTriangle, Flag, Trash2, Reply, ExternalLink } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { Badge } from "@/components/ui/badge"

export default function PhishingSimulation() {
  return (
    <div className="min-h-screen bg-gray-50">
      {/* Navigation */}
      <nav className="bg-blue-600 text-white shadow-lg">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center space-x-4">
              <Shield className="h-8 w-8" />
              <div>
                <h1 className="text-xl font-bold">AttackSim</h1>
                <p className="text-xs text-blue-100">Phishing Email Simulation</p>
              </div>
            </div>

            <div className="flex items-center space-x-4">
              <Badge variant="secondary" className="bg-orange-100 text-orange-800">
                <AlertTriangle className="h-3 w-3 mr-1" />
                Training Mode
              </Badge>
              <Button variant="ghost" className="text-white hover:bg-blue-700">
                Exit Simulation
              </Button>
            </div>
          </div>
        </div>
      </nav>

      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Educational Alert */}
        <Alert className="mb-6 border-orange-200 bg-orange-50">
          <AlertTriangle className="h-5 w-5 text-orange-600" />
          <AlertDescription className="text-orange-800">
            <strong>Educational Simulation:</strong> This is a training exercise. Analyze the email below and choose the
            appropriate action.
          </AlertDescription>
        </Alert>

        {/* Email Container */}
        <Card className="border-0 shadow-lg">
          <CardHeader className="bg-white border-b">
            <div className="flex items-center justify-between">
              <CardTitle className="text-lg">Email Client - Inbox</CardTitle>
              <div className="flex space-x-2">
                <Badge variant="outline" className="text-xs">
                  Unread
                </Badge>
                <Badge variant="destructive" className="text-xs">
                  High Priority
                </Badge>
              </div>
            </div>
          </CardHeader>

          <CardContent className="p-0">
            {/* Email Header */}
            <div className="bg-gray-50 p-6 border-b">
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-600">From:</p>
                    <p className="font-medium text-red-600">security-alert@paypaI-security.com</p>
                    <p className="text-xs text-gray-500">via suspicious-sender.net</p>
                  </div>
                  <div className="text-right">
                    <p className="text-sm text-gray-600">Date:</p>
                    <p className="font-medium">Jan 15, 2024 2:47 PM</p>
                  </div>
                </div>

                <div>
                  <p className="text-sm text-gray-600">Subject:</p>
                  <p className="font-medium text-lg">🚨 URGENT: Your PayPal Account Has Been Limited</p>
                </div>

                <div>
                  <p className="text-sm text-gray-600">To:</p>
                  <p className="font-medium">your.email@example.com</p>
                </div>
              </div>
            </div>

            {/* Email Body */}
            <div className="p-6">
              <div className="prose max-w-none">
                <div className="bg-blue-50 p-4 rounded-lg mb-4 border-l-4 border-blue-400">
                  <h3 className="text-lg font-bold text-blue-900 mb-2">Account Security Alert</h3>
                  <p className="text-blue-800">Dear Valued Customer,</p>
                </div>

                <p className="mb-4">
                  We have detected unusual activity on your PayPal account. For your security, we have temporarily
                  limited your account access.
                </p>

                <div className="bg-red-50 p-4 rounded-lg mb-4 border border-red-200">
                  <p className="text-red-800 font-medium">⚠️ Immediate Action Required</p>
                  <p className="text-red-700 text-sm mt-1">
                    Your account will be permanently suspended in 24 hours if not verified.
                  </p>
                </div>

                <p className="mb-4">
                  To restore full access to your account, please verify your identity by clicking the link below and
                  providing the requested information:
                </p>

                <div className="text-center my-6">
                  <Button className="bg-blue-600 hover:bg-blue-700 text-white px-8 py-3">
                    <ExternalLink className="h-4 w-4 mr-2" />
                    Verify Account Now
                  </Button>
                  <p className="text-xs text-gray-500 mt-2">
                    Link: https://paypaI-verification.secure-login.net/verify?id=abc123
                  </p>
                </div>

                <p className="text-sm text-gray-600 mb-4">
                  If you do not verify within 24 hours, your account will be permanently closed and all funds will be
                  frozen.
                </p>

                <div className="border-t pt-4 mt-6">
                  <p className="text-sm text-gray-600">Thank you for your immediate attention to this matter.</p>
                  <p className="text-sm text-gray-600 mt-2">
                    PayPal Security Team
                    <br />
                    Customer Protection Services
                  </p>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Action Buttons */}
        <div className="mt-8">
          <h3 className="text-lg font-semibold mb-4">What would you do with this email?</h3>
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-4">
            <Button variant="destructive" className="h-auto p-4 flex flex-col items-center space-y-2">
              <Flag className="h-6 w-6" />
              <span>Report as Spam</span>
              <span className="text-xs opacity-80">Mark as phishing</span>
            </Button>

            <Button
              variant="outline"
              className="h-auto p-4 flex flex-col items-center space-y-2 border-red-200 text-red-600 hover:bg-red-50 bg-transparent"
            >
              <ExternalLink className="h-6 w-6" />
              <span>Click Link</span>
              <span className="text-xs opacity-80">Verify account</span>
            </Button>

            <Button variant="outline" className="h-auto p-4 flex flex-col items-center space-y-2 bg-transparent">
              <Trash2 className="h-6 w-6" />
              <span>Delete</span>
              <span className="text-xs opacity-80">Remove email</span>
            </Button>

            <Button variant="outline" className="h-auto p-4 flex flex-col items-center space-y-2 bg-transparent">
              <Reply className="h-6 w-6" />
              <span>Reply</span>
              <span className="text-xs opacity-80">Ask for clarification</span>
            </Button>
          </div>
        </div>

        {/* Warning Indicators */}
        <Card className="mt-8 border-orange-200 bg-orange-50">
          <CardHeader>
            <CardTitle className="text-orange-800 flex items-center">
              <AlertTriangle className="h-5 w-5 mr-2" />
              Red Flags to Look For
            </CardTitle>
          </CardHeader>
          <CardContent>
            <ul className="space-y-2 text-orange-800">
              <li className="flex items-start">
                <span className="text-red-500 mr-2">•</span>
                Suspicious sender domain (paypaI-security.com with capital 'I' instead of 'l')
              </li>
              <li className="flex items-start">
                <span className="text-red-500 mr-2">•</span>
                Urgent language creating false sense of emergency
              </li>
              <li className="flex items-start">
                <span className="text-red-500 mr-2">•</span>
                Threatening account closure to pressure quick action
              </li>
              <li className="flex items-start">
                <span className="text-red-500 mr-2">•</span>
                Suspicious verification link leading to non-PayPal domain
              </li>
              <li className="flex items-start">
                <span className="text-red-500 mr-2">•</span>
                Generic greeting instead of personalized message
              </li>
            </ul>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
