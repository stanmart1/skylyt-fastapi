import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from '@/components/ui/dialog';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Textarea } from '@/components/ui/textarea';
import { Star, MessageSquare, CheckCircle, XCircle, Eye, Reply, Filter, Search } from 'lucide-react';
import { apiService } from '@/services/api';
import { useAuth } from '@/contexts/AuthContext';
import { ConfirmDialog } from '@/components/ui/ConfirmDialog';
import { useToast } from '@/hooks/useToast';

interface Review {
  id: number;
  hotel_id?: number;
  car_id?: number;
  hotel_name?: string;
  car_name?: string;
  user_name: string;
  user_email: string;
  rating: number;
  comment: string;
  status: 'pending' | 'approved' | 'rejected';
  created_at: string;
  admin_response?: string;
  response_date?: string;
}

export const ReviewManagement: React.FC = () => {
  const { hasPermission } = useAuth();
  const { toast } = useToast();
  const [reviews, setReviews] = useState<Review[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedReview, setSelectedReview] = useState<Review | null>(null);
  const [isDetailModalOpen, setIsDetailModalOpen] = useState(false);
  const [isResponseModalOpen, setIsResponseModalOpen] = useState(false);
  const [responseText, setResponseText] = useState('');
  const [filters, setFilters] = useState({
    status: '',
    rating: '',
    search: ''
  });
  const [confirmDialog, setConfirmDialog] = useState<{
    open: boolean;
    title: string;
    description: string;
    action: () => void;
  }>({ open: false, title: '', description: '', action: () => {} });

  useEffect(() => {
    fetchReviews();
  }, [filters]);

  const fetchReviews = async () => {
    try {
      setLoading(true);
      const params = new URLSearchParams();
      if (filters.status) params.append('status', filters.status);
      if (filters.rating) params.append('rating', filters.rating);
      if (filters.search) params.append('search', filters.search);
      
      const data = await apiService.request(`/admin/reviews?${params.toString()}`);
      setReviews(data || []);
    } catch (error) {
      console.error('Failed to fetch reviews:', error);
      toast({
        title: 'Error',
        description: 'Failed to fetch reviews',
        variant: 'error'
      });
    } finally {
      setLoading(false);
    }
  };

  const handleApproveReview = (reviewId: number) => {
    setConfirmDialog({
      open: true,
      title: 'Approve Review',
      description: 'Are you sure you want to approve this review?',
      action: () => updateReviewStatus(reviewId, 'approved')
    });
  };

  const handleRejectReview = (reviewId: number) => {
    setConfirmDialog({
      open: true,
      title: 'Reject Review',
      description: 'Are you sure you want to reject this review?',
      action: () => updateReviewStatus(reviewId, 'rejected')
    });
  };

  const updateReviewStatus = async (reviewId: number, status: string) => {
    try {
      await apiService.request(`/admin/reviews/${reviewId}/status`, {
        method: 'PUT',
        body: JSON.stringify({ status })
      });
      
      toast({
        title: 'Success',
        description: `Review ${status} successfully`,
        variant: 'success'
      });
      
      fetchReviews();
    } catch (error) {
      console.error('Failed to update review status:', error);
      toast({
        title: 'Error',
        description: 'Failed to update review status',
        variant: 'error'
      });
    }
  };

  const handleAddResponse = (review: Review) => {
    setSelectedReview(review);
    setResponseText(review.admin_response || '');
    setIsResponseModalOpen(true);
  };

  const handleSaveResponse = async () => {
    if (!selectedReview) return;
    
    try {
      await apiService.request(`/admin/reviews/${selectedReview.id}/response`, {
        method: 'POST',
        body: JSON.stringify({ response: responseText })
      });
      
      toast({
        title: 'Success',
        description: 'Response added successfully',
        variant: 'success'
      });
      
      setIsResponseModalOpen(false);
      fetchReviews();
    } catch (error) {
      console.error('Failed to add response:', error);
      toast({
        title: 'Error',
        description: 'Failed to add response',
        variant: 'error'
      });
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'approved': return 'bg-green-100 text-green-800';
      case 'rejected': return 'bg-red-100 text-red-800';
      case 'pending': return 'bg-yellow-100 text-yellow-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const renderStars = (rating: number) => {
    return [...Array(5)].map((_, i) => (
      <Star
        key={i}
        className={`h-4 w-4 ${i < rating ? 'text-yellow-400 fill-current' : 'text-gray-300'}`}
      />
    ));
  };

  return (
    <div className="space-y-6">
      {/* Filters */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Filter className="h-5 w-5" />
            Filters
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
              <Input
                placeholder="Search reviews..."
                value={filters.search}
                onChange={(e) => setFilters({ ...filters, search: e.target.value })}
                className="pl-10"
              />
            </div>
            
            <Select value={filters.status || 'all'} onValueChange={(value) => setFilters({ ...filters, status: value === 'all' ? '' : value })}>
              <SelectTrigger>
                <SelectValue placeholder="All Statuses" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Statuses</SelectItem>
                <SelectItem value="pending">Pending</SelectItem>
                <SelectItem value="approved">Approved</SelectItem>
                <SelectItem value="rejected">Rejected</SelectItem>
              </SelectContent>
            </Select>

            <Select value={filters.rating || 'all'} onValueChange={(value) => setFilters({ ...filters, rating: value === 'all' ? '' : value })}>
              <SelectTrigger>
                <SelectValue placeholder="All Ratings" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Ratings</SelectItem>
                <SelectItem value="5">5 Stars</SelectItem>
                <SelectItem value="4">4 Stars</SelectItem>
                <SelectItem value="3">3 Stars</SelectItem>
                <SelectItem value="2">2 Stars</SelectItem>
                <SelectItem value="1">1 Star</SelectItem>
              </SelectContent>
            </Select>

            <Button 
              variant="outline" 
              onClick={() => setFilters({ status: '', rating: '', search: '' })}
            >
              Clear Filters
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Reviews List */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <MessageSquare className="h-5 w-5" />
            Reviews ({reviews.length})
          </CardTitle>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="space-y-4">
              {[...Array(5)].map((_, i) => (
                <div key={i} className="animate-pulse h-24 bg-gray-200 rounded" />
              ))}
            </div>
          ) : reviews.length === 0 ? (
            <div className="text-center py-8">
              <MessageSquare className="h-12 w-12 text-gray-400 mx-auto mb-4" />
              <p className="text-gray-600">No reviews found</p>
            </div>
          ) : (
            <div className="space-y-4">
              {reviews.map((review) => (
                <div key={review.id} className="border rounded-lg p-4">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-2">
                        <h3 className="font-semibold">{review.user_name}</h3>
                        <div className="flex items-center gap-1">
                          {renderStars(review.rating)}
                        </div>
                        <Badge className={getStatusColor(review.status)}>
                          {review.status}
                        </Badge>
                      </div>
                      
                      <p className="text-sm text-gray-600 mb-2">
                        {review.hotel_name || review.car_name} • {review.user_email}
                      </p>
                      
                      <p className="text-gray-800 mb-2">{review.comment}</p>
                      
                      {review.admin_response && (
                        <div className="bg-blue-50 p-3 rounded-lg mt-2">
                          <p className="text-sm font-medium text-blue-800">Admin Response:</p>
                          <p className="text-sm text-blue-700">{review.admin_response}</p>
                          {review.response_date && (
                            <p className="text-xs text-blue-600 mt-1">
                              {new Date(review.response_date).toLocaleDateString()}
                            </p>
                          )}
                        </div>
                      )}
                      
                      <p className="text-xs text-gray-500 mt-2">
                        {new Date(review.created_at).toLocaleDateString()}
                      </p>
                    </div>
                    
                    <div className="flex items-center gap-2 ml-4">
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => {
                          setSelectedReview(review);
                          setIsDetailModalOpen(true);
                        }}
                      >
                        <Eye className="h-3 w-3" />
                      </Button>
                      
                      {hasPermission('reviews.respond') && (
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => handleAddResponse(review)}
                        >
                          <Reply className="h-3 w-3" />
                        </Button>
                      )}
                      
                      {review.status === 'pending' && hasPermission('reviews.moderate') && (
                        <>
                          <Button
                            size="sm"
                            onClick={() => handleApproveReview(review.id)}
                            className="bg-green-600 hover:bg-green-700"
                          >
                            <CheckCircle className="h-3 w-3" />
                          </Button>
                          <Button
                            size="sm"
                            variant="destructive"
                            onClick={() => handleRejectReview(review.id)}
                          >
                            <XCircle className="h-3 w-3" />
                          </Button>
                        </>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Review Detail Modal */}
      <Dialog open={isDetailModalOpen} onOpenChange={setIsDetailModalOpen}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle>Review Details</DialogTitle>
            <DialogDescription>
              View detailed information about this customer review.
            </DialogDescription>
          </DialogHeader>
          {selectedReview && (
            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label className="text-sm font-medium text-gray-600">Customer</Label>
                  <p className="text-sm">{selectedReview.user_name}</p>
                </div>
                <div>
                  <Label className="text-sm font-medium text-gray-600">Email</Label>
                  <p className="text-sm">{selectedReview.user_email}</p>
                </div>
                <div>
                  <Label className="text-sm font-medium text-gray-600">Item</Label>
                  <p className="text-sm">{selectedReview.hotel_name || selectedReview.car_name}</p>
                </div>
                <div>
                  <Label className="text-sm font-medium text-gray-600">Rating</Label>
                  <div className="flex items-center gap-1">
                    {renderStars(selectedReview.rating)}
                  </div>
                </div>
              </div>
              
              <div>
                <Label className="text-sm font-medium text-gray-600">Review</Label>
                <p className="text-sm bg-gray-50 p-3 rounded">{selectedReview.comment}</p>
              </div>
              
              {selectedReview.admin_response && (
                <div>
                  <Label className="text-sm font-medium text-gray-600">Admin Response</Label>
                  <p className="text-sm bg-blue-50 p-3 rounded">{selectedReview.admin_response}</p>
                </div>
              )}
              
              <div className="flex gap-2 pt-4">
                <Button variant="outline" onClick={() => setIsDetailModalOpen(false)}>
                  Close
                </Button>
              </div>
            </div>
          )}
        </DialogContent>
      </Dialog>

      {/* Response Modal */}
      <Dialog open={isResponseModalOpen} onOpenChange={setIsResponseModalOpen}>
        <DialogContent className="max-w-md">
          <DialogHeader>
            <DialogTitle>Add Admin Response</DialogTitle>
            <DialogDescription>
              Respond to this customer review with an official admin message.
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4">
            <div>
              <Label htmlFor="response">Response</Label>
              <Textarea
                id="response"
                value={responseText}
                onChange={(e) => setResponseText(e.target.value)}
                placeholder="Enter your response to this review..."
                rows={4}
              />
            </div>
            
            <div className="flex gap-2 pt-4">
              <Button onClick={handleSaveResponse}>
                Save Response
              </Button>
              <Button variant="outline" onClick={() => setIsResponseModalOpen(false)}>
                Cancel
              </Button>
            </div>
          </div>
        </DialogContent>
      </Dialog>

      {/* Confirm Dialog */}
      <ConfirmDialog
        open={confirmDialog.open}
        onOpenChange={(open) => setConfirmDialog({ ...confirmDialog, open })}
        title={confirmDialog.title}
        description={confirmDialog.description}
        onConfirm={confirmDialog.action}
      />
    </div>
  );
};