import { Shield, Mail, Lock, Link, TrendingUp, Calendar, CheckCircle, AlertTriangle, Clock } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Progress } from "@/components/ui/progress"

export default function UserDashboard() {
  const userStats = {
    totalInteractions: 47,
    successfulDetections: 35,
    detectionRate: 74,
    currentStreak: 5,
  }

  const recentActivity = [
    {
      type: "Phishing Email",
      date: "2024-01-15",
      result: "detected",
      description: "Suspicious PayPal notification",
    },
    {
      type: "Fake Login",
      date: "2024-01-14",
      result: "missed",
      description: "Facebook login page simulation",
    },
    {
      type: "Suspicious Link",
      date: "2024-01-13",
      result: "detected",
      description: "Shortened URL analysis",
    },
    {
      type: "Phishing Email",
      date: "2024-01-12",
      result: "detected",
      description: "Bank security alert",
    },
  ]

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
                <p className="text-xs text-blue-100">Simulated threats. Real awareness.</p>
              </div>
            </div>

            <div className="hidden md:flex items-center space-x-8">
              <a href="/" className="hover:text-blue-200 transition-colors">
                Home
              </a>
              <a href="/dashboard" className="text-blue-200 font-medium">
                Dashboard
              </a>
              <a href="/about" className="hover:text-blue-200 transition-colors">
                About
              </a>
              <a href="/help" className="hover:text-blue-200 transition-colors">
                Help
              </a>
            </div>

            <div className="flex items-center space-x-4">
              <Button variant="ghost" className="text-white hover:bg-blue-700">
                Profile
              </Button>
            </div>
          </div>
        </div>
      </nav>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">Welcome back, Alex!</h1>
              <p className="text-gray-600 mt-1">Continue your cybersecurity training journey</p>
            </div>
            <Badge variant="secondary" className="bg-green-100 text-green-800 px-3 py-1">
              <CheckCircle className="h-4 w-4 mr-1" />
              Active Training
            </Badge>
          </div>
        </div>

        {/* Stats Overview */}
        <div className="grid md:grid-cols-4 gap-6 mb-8">
          <Card className="border-0 shadow-md">
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-gray-600">Total Interactions</CardTitle>
              <div className="text-2xl font-bold text-blue-600">{userStats.totalInteractions}</div>
            </CardHeader>
            <CardContent>
              <p className="text-xs text-gray-500">+3 from last week</p>
            </CardContent>
          </Card>

          <Card className="border-0 shadow-md">
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-gray-600">Successful Detections</CardTitle>
              <div className="text-2xl font-bold text-green-600">{userStats.successfulDetections}</div>
            </CardHeader>
            <CardContent>
              <p className="text-xs text-gray-500">+5 from last week</p>
            </CardContent>
          </Card>

          <Card className="border-0 shadow-md">
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-gray-600">Detection Rate</CardTitle>
              <div className="text-2xl font-bold text-orange-600">{userStats.detectionRate}%</div>
            </CardHeader>
            <CardContent>
              <Progress value={userStats.detectionRate} className="h-2" />
              <p className="text-xs text-gray-500 mt-1">+8% improvement</p>
            </CardContent>
          </Card>

          <Card className="border-0 shadow-md">
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-gray-600">Current Streak</CardTitle>
              <div className="text-2xl font-bold text-cyan-600">{userStats.currentStreak}</div>
            </CardHeader>
            <CardContent>
              <p className="text-xs text-gray-500">Days in a row</p>
            </CardContent>
          </Card>
        </div>

        <div className="grid lg:grid-cols-3 gap-8">
          {/* Recent Activity */}
          <div className="lg:col-span-2">
            <Card className="border-0 shadow-md">
              <CardHeader>
                <CardTitle className="flex items-center">
                  <Clock className="h-5 w-5 mr-2" />
                  Recent Activity
                </CardTitle>
                <CardDescription>Your latest simulation interactions</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {recentActivity.map((activity, index) => (
                    <div key={index} className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                      <div className="flex items-center space-x-3">
                        <div
                          className={`p-2 rounded-full ${
                            activity.type === "Phishing Email"
                              ? "bg-red-100"
                              : activity.type === "Fake Login"
                                ? "bg-orange-100"
                                : "bg-blue-100"
                          }`}
                        >
                          {activity.type === "Phishing Email" && <Mail className="h-4 w-4 text-red-600" />}
                          {activity.type === "Fake Login" && <Lock className="h-4 w-4 text-orange-600" />}
                          {activity.type === "Suspicious Link" && <Link className="h-4 w-4 text-blue-600" />}
                        </div>
                        <div>
                          <p className="font-medium text-gray-900">{activity.type}</p>
                          <p className="text-sm text-gray-600">{activity.description}</p>
                          <p className="text-xs text-gray-500">{activity.date}</p>
                        </div>
                      </div>
                      <Badge
                        variant={activity.result === "detected" ? "default" : "destructive"}
                        className={
                          activity.result === "detected" ? "bg-green-100 text-green-800" : "bg-red-100 text-red-800"
                        }
                      >
                        {activity.result === "detected" ? (
                          <>
                            <CheckCircle className="h-3 w-3 mr-1" />
                            Detected
                          </>
                        ) : (
                          <>
                            <AlertTriangle className="h-3 w-3 mr-1" />
                            Missed
                          </>
                        )}
                      </Badge>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Quick Actions */}
          <div>
            <Card className="border-0 shadow-md">
              <CardHeader>
                <CardTitle>Quick Actions</CardTitle>
                <CardDescription>Manage your training experience</CardDescription>
              </CardHeader>
              <CardContent className="space-y-3">
                <Button className="w-full justify-start bg-transparent" variant="outline">
                  <Shield className="h-4 w-4 mr-2" />
                  View Profile
                </Button>
                <Button className="w-full justify-start bg-transparent" variant="outline">
                  <TrendingUp className="h-4 w-4 mr-2" />
                  Training Settings
                </Button>
                <Button className="w-full justify-start bg-transparent" variant="outline">
                  <Calendar className="h-4 w-4 mr-2" />
                  Schedule Training
                </Button>
                <Button className="w-full justify-start bg-blue-600 hover:bg-blue-700 text-white">
                  Start New Simulation
                </Button>
              </CardContent>
            </Card>

            {/* Progress Chart Placeholder */}
            <Card className="border-0 shadow-md mt-6">
              <CardHeader>
                <CardTitle className="text-lg">Progress Over Time</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="h-32 bg-gradient-to-r from-blue-100 to-green-100 rounded-lg flex items-center justify-center">
                  <TrendingUp className="h-8 w-8 text-blue-600" />
                </div>
                <p className="text-sm text-gray-600 mt-2 text-center">
                  Your detection rate has improved by 15% this month
                </p>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  )
}
