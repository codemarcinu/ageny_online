import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Textarea } from '@/components/ui/textarea';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { 
  Trophy, 
  Clock, 
  ChefHat, 
  Target, 
  Star, 
  Timer,
  Award,
  Flame,
  Sparkles
} from 'lucide-react';

interface CookingChallenge {
  challenge_id: number;
  title: string;
  description: string;
  difficulty: string;
  ingredients: string[];
  instructions: string[];
  time_limit: number;
  points_reward: number;
  tips: string[];
}

const CookingChallengesSection: React.FC = () => {
  const [challenge, setChallenge] = useState<CookingChallenge | null>(null);
  const [loading, setLoading] = useState(false);
  const [completedChallenges, setCompletedChallenges] = useState<number[]>([]);
  const [currentChallenge, setCurrentChallenge] = useState<{
    startTime: number;
    timeLeft: number;
    completedSteps: number[];
  } | null>(null);

  const [challengeForm, setChallengeForm] = useState({
    difficulty: 'łatwy',
    cuisine_type: '',
    available_ingredients: '',
    time_limit: 60
  });

  const getDifficultyColor = (difficulty: string) => {
    switch (difficulty.toLowerCase()) {
      case 'łatwy':
        return 'bg-green-100 text-green-800';
      case 'średni':
        return 'bg-yellow-100 text-yellow-800';
      case 'trudny':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const createChallenge = async () => {
    setLoading(true);
    try {
      const response = await fetch('/api/v2/cooking/challenges', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          ...challengeForm,
          available_ingredients: challengeForm.available_ingredients ? 
            challengeForm.available_ingredients.split(',').map(s => s.trim()) : undefined
        }),
      });

      if (response.ok) {
        const data = await response.json();
        setChallenge(data);
        setCurrentChallenge({
          startTime: Date.now(),
          timeLeft: data.time_limit * 60, // Convert to seconds
          completedSteps: []
        });
      } else {
        console.error('Failed to create challenge');
      }
    } catch (error) {
      console.error('Error creating challenge:', error);
    } finally {
      setLoading(false);
    }
  };

  const startChallenge = () => {
    if (challenge) {
      setCurrentChallenge({
        startTime: Date.now(),
        timeLeft: challenge.time_limit * 60,
        completedSteps: []
      });
    }
  };

  const completeStep = (stepIndex: number) => {
    if (currentChallenge && !currentChallenge.completedSteps.includes(stepIndex)) {
      setCurrentChallenge(prev => ({
        ...prev!,
        completedSteps: [...prev!.completedSteps, stepIndex]
      }));
    }
  };

  const completeChallenge = () => {
    if (challenge && currentChallenge) {
      setCompletedChallenges(prev => [...prev, challenge.challenge_id]);
      setCurrentChallenge(null);
      // Here you would typically send the completion to the backend
      console.log('Challenge completed!');
    }
  };

  const getTimeLeft = () => {
    if (!currentChallenge) return 0;
    const elapsed = Math.floor((Date.now() - currentChallenge.startTime) / 1000);
    return Math.max(0, currentChallenge.timeLeft - elapsed);
  };

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const getProgress = () => {
    if (!challenge || !currentChallenge) return 0;
    return (currentChallenge.completedSteps.length / challenge.instructions.length) * 100;
  };

  // Sample challenges for demonstration
  const sampleChallenges = [
    {
      id: 1,
      title: "Pierwsze Kroki w Kuchni",
      difficulty: "łatwy",
      description: "Przygotuj prostą kanapkę z warzywami",
      time_limit: 15,
      points: 50
    },
    {
      id: 2,
      title: "Mistrz Jajecznicy",
      difficulty: "średni",
      description: "Usmaż idealną jajecznicę z dodatkami",
      time_limit: 20,
      points: 100
    },
    {
      id: 3,
      title: "Pizza Domowa",
      difficulty: "trudny",
      description: "Przygotuj pizzę od podstaw",
      time_limit: 90,
      points: 200
    }
  ];

  return (
    <div className="space-y-6">
      <div className="flex items-center space-x-2">
        <Trophy className="h-6 w-6 text-yellow-600" />
        <h2 className="text-2xl font-bold text-gray-900">Wyzwania Kulinarne</h2>
      </div>

      {/* Challenge Creation */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <ChefHat className="h-5 w-5" />
            <span>Stwórz Wyzwanie</span>
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="difficulty">Poziom Trudności</Label>
              <Select
                value={challengeForm.difficulty}
                onValueChange={(value) => setChallengeForm(prev => ({ ...prev, difficulty: value }))}
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="łatwy">Łatwy</SelectItem>
                  <SelectItem value="średni">Średni</SelectItem>
                  <SelectItem value="trudny">Trudny</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-2">
              <Label htmlFor="cuisine">Typ Kuchni</Label>
              <Input
                id="cuisine"
                placeholder="np. włoska, polska, azjatycka..."
                value={challengeForm.cuisine_type}
                onChange={(e) => setChallengeForm(prev => ({ ...prev, cuisine_type: e.target.value }))}
              />
            </div>
          </div>

          <div className="space-y-2">
            <Label htmlFor="ingredients">Dostępne Składniki</Label>
            <Textarea
              id="ingredients"
              placeholder="np. jajka, mąka, pomidory, ser... (oddzielone przecinkami)"
              value={challengeForm.available_ingredients}
              onChange={(e) => setChallengeForm(prev => ({ ...prev, available_ingredients: e.target.value }))}
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="time-limit">Limit Czasu (minuty)</Label>
            <Input
              id="time-limit"
              type="number"
              value={challengeForm.time_limit}
              onChange={(e) => setChallengeForm(prev => ({ ...prev, time_limit: parseInt(e.target.value) }))}
              min="15"
              max="180"
            />
          </div>

          <Button 
            onClick={createChallenge} 
            disabled={loading}
            className="w-full"
          >
            {loading ? 'Tworzę wyzwanie...' : 'Stwórz Wyzwanie'}
          </Button>
        </CardContent>
      </Card>

      {/* Current Challenge */}
      {challenge && (
        <Card className="border-2 border-blue-500">
          <CardHeader>
            <CardTitle className="flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <Target className="h-5 w-5 text-blue-600" />
                <span>{challenge.title}</span>
              </div>
              <Badge className={getDifficultyColor(challenge.difficulty)}>
                {challenge.difficulty}
              </Badge>
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-6">
            <p className="text-gray-600">{challenge.description}</p>

            {/* Timer and Progress */}
            {currentChallenge && (
              <div className="space-y-4">
                <div className="flex justify-between items-center">
                  <div className="flex items-center space-x-2">
                    <Timer className="h-5 w-5 text-red-600" />
                    <span className="font-semibold">Pozostały czas: {formatTime(getTimeLeft())}</span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <Star className="h-5 w-5 text-yellow-600" />
                    <span className="font-semibold">{challenge.points_reward} punktów</span>
                  </div>
                </div>

                <div className="space-y-2">
                  <div className="flex justify-between text-sm">
                    <span>Postęp</span>
                    <span>{Math.round(getProgress())}%</span>
                  </div>
                  <Progress value={getProgress()} className="h-2" />
                </div>
              </div>
            )}

            {/* Ingredients */}
            <div className="space-y-2">
              <h4 className="font-semibold flex items-center space-x-2">
                <Flame className="h-4 w-4" />
                <span>Potrzebne Składniki</span>
              </h4>
              <div className="flex flex-wrap gap-2">
                {challenge.ingredients.map((ingredient, index) => (
                  <Badge key={index} variant="outline">
                    {ingredient}
                  </Badge>
                ))}
              </div>
            </div>

            {/* Instructions */}
            <div className="space-y-4">
              <h4 className="font-semibold">Instrukcje</h4>
              <div className="space-y-3">
                {challenge.instructions.map((instruction, index) => (
                  <div
                    key={index}
                    className={`flex items-start space-x-3 p-3 rounded-lg border ${
                      currentChallenge?.completedSteps.includes(index)
                        ? 'bg-green-50 border-green-200'
                        : 'bg-gray-50 border-gray-200'
                    }`}
                  >
                    <div className={`w-6 h-6 rounded-full flex items-center justify-center text-sm font-semibold ${
                      currentChallenge?.completedSteps.includes(index)
                        ? 'bg-green-500 text-white'
                        : 'bg-gray-300 text-gray-600'
                    }`}>
                      {index + 1}
                    </div>
                    <div className="flex-1">
                      <p className="text-sm">{instruction}</p>
                    </div>
                    {currentChallenge && !currentChallenge.completedSteps.includes(index) && (
                      <Button
                        size="sm"
                        onClick={() => completeStep(index)}
                        className="ml-2"
                      >
                        Ukończ
                      </Button>
                    )}
                    {currentChallenge?.completedSteps.includes(index) && (
                      <Award className="h-5 w-5 text-green-600 ml-2" />
                    )}
                  </div>
                ))}
              </div>
            </div>

            {/* Tips */}
            {challenge.tips.length > 0 && (
              <div className="space-y-2">
                <h4 className="font-semibold flex items-center space-x-2">
                  <Sparkles className="h-4 w-4" />
                  <span>Wskazówki</span>
                </h4>
                <div className="space-y-2">
                  {challenge.tips.map((tip, index) => (
                    <div key={index} className="flex items-start space-x-2 p-2 bg-blue-50 rounded">
                      <Sparkles className="h-4 w-4 text-blue-600 mt-0.5 flex-shrink-0" />
                      <span className="text-sm">{tip}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Action Buttons */}
            <div className="flex space-x-4">
              {!currentChallenge ? (
                <Button onClick={startChallenge} className="flex-1">
                  Rozpocznij Wyzwanie
                </Button>
              ) : (
                <>
                  <Button 
                    onClick={completeChallenge}
                    disabled={getProgress() < 100}
                    className="flex-1"
                  >
                    {getProgress() < 100 ? 'Ukończ wszystkie kroki' : 'Ukończ Wyzwanie!'}
                  </Button>
                  <Button 
                    variant="outline"
                    onClick={() => setCurrentChallenge(null)}
                  >
                    Przerwij
                  </Button>
                </>
              )}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Sample Challenges */}
      <div className="space-y-4">
        <h3 className="text-lg font-semibold">Przykładowe Wyzwania</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {sampleChallenges.map((sampleChallenge) => (
            <Card 
              key={sampleChallenge.id}
              className={`cursor-pointer transition-all hover:shadow-lg ${
                completedChallenges.includes(sampleChallenge.id) 
                  ? 'border-green-500 bg-green-50' 
                  : ''
              }`}
            >
              <CardContent className="pt-4">
                <div className="flex justify-between items-start mb-2">
                  <h4 className="font-semibold">{sampleChallenge.title}</h4>
                  <Badge className={getDifficultyColor(sampleChallenge.difficulty)}>
                    {sampleChallenge.difficulty}
                  </Badge>
                </div>
                <p className="text-sm text-gray-600 mb-3">{sampleChallenge.description}</p>
                <div className="flex justify-between items-center">
                  <div className="flex items-center space-x-1 text-sm text-gray-500">
                    <Clock className="h-4 w-4" />
                    <span>{sampleChallenge.time_limit} min</span>
                  </div>
                  <div className="flex items-center space-x-1 text-sm text-yellow-600">
                    <Star className="h-4 w-4" />
                    <span>{sampleChallenge.points}</span>
                  </div>
                </div>
                {completedChallenges.includes(sampleChallenge.id) && (
                  <div className="mt-2 flex items-center space-x-1 text-green-600">
                    <Award className="h-4 w-4" />
                    <span className="text-sm font-medium">Ukończone!</span>
                  </div>
                )}
              </CardContent>
            </Card>
          ))}
        </div>
      </div>

      {/* Statistics */}
      <Card>
        <CardHeader>
          <CardTitle>Twoje Osiągnięcia</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-center">
            <div>
              <div className="text-2xl font-bold text-blue-600">{completedChallenges.length}</div>
              <div className="text-sm text-gray-600">Ukończone wyzwania</div>
            </div>
            <div>
              <div className="text-2xl font-bold text-green-600">
                {completedChallenges.length * 100}
              </div>
              <div className="text-sm text-gray-600">Zdobyte punkty</div>
            </div>
            <div>
              <div className="text-2xl font-bold text-yellow-600">
                {Math.floor(completedChallenges.length / 3)}
              </div>
              <div className="text-sm text-gray-600">Poziomy trudności</div>
            </div>
            <div>
              <div className="text-2xl font-bold text-purple-600">
                {Math.floor(completedChallenges.length / 5)}
              </div>
              <div className="text-sm text-gray-600">Osiągnięcia</div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default CookingChallengesSection; 