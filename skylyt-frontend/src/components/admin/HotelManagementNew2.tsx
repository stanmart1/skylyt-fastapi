      {/* Hotel Modal */}
      <Dialog open={isModalOpen} onOpenChange={setIsModalOpen}>
        <DialogContent className="max-w-4xl max-h-[80vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>{editingHotel ? 'Edit Hotel' : 'Add New Hotel'}</DialogTitle>
            <DialogDescription>
              {editingHotel ? 'Update the hotel details below.' : 'Add a new hotel property to your portfolio.'}
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-6">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label htmlFor="name">Hotel Name</Label>
                <Input id="name" value={hotelForm.name} onChange={(e) => setHotelForm({...hotelForm, name: e.target.value})} />
              </div>
              <div>
                <Label htmlFor="star_rating">Star Rating</Label>
                <Select value={hotelForm.star_rating.toString()} onValueChange={(value) => setHotelForm({...hotelForm, star_rating: Number(value)})}>
                  <SelectTrigger>
                    <SelectValue placeholder="Select rating" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="1">1 Star</SelectItem>
                    <SelectItem value="2">2 Stars</SelectItem>
                    <SelectItem value="3">3 Stars</SelectItem>
                    <SelectItem value="4">4 Stars</SelectItem>
                    <SelectItem value="5">5 Stars</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>
            
            <div className="grid grid-cols-4 gap-4">
              <div>
                <Label htmlFor="location">Street Address</Label>
                <Input id="location" value={hotelForm.location} onChange={(e) => setHotelForm({...hotelForm, location: e.target.value})} />
              </div>
              <div>
                <Label htmlFor="city">City</Label>
                <Input id="city" value={hotelForm.city} onChange={(e) => setHotelForm({...hotelForm, city: e.target.value})} />
              </div>
              <div>
                <Label htmlFor="state">State</Label>
                <Input id="state" value={hotelForm.state} onChange={(e) => setHotelForm({...hotelForm, state: e.target.value})} />
              </div>
              <div>
                <Label htmlFor="country">Country</Label>
                <Input id="country" value={hotelForm.country} onChange={(e) => setHotelForm({...hotelForm, country: e.target.value})} />
              </div>
            </div>
            
            <div className="grid grid-cols-3 gap-4">
              <div>
                <Label htmlFor="price_per_night">Base Price per Night</Label>
                <Input id="price_per_night" type="number" value={hotelForm.price_per_night} onChange={(e) => setHotelForm({...hotelForm, price_per_night: Number(e.target.value)})} />
              </div>
              <div>
                <Label htmlFor="room_count">Total Rooms</Label>
                <Input id="room_count" type="number" value={hotelForm.room_count} onChange={(e) => setHotelForm({...hotelForm, room_count: Number(e.target.value)})} />
              </div>
              <div className="flex items-end">
                <div className="flex items-center space-x-2">
                  <Switch
                    id="is_available"
                    checked={hotelForm.is_available}
                    onCheckedChange={(checked) => setHotelForm({...hotelForm, is_available: checked})}
                  />
                  <Label htmlFor="is_available">Available for Booking</Label>
                </div>
              </div>
            </div>
            
            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label htmlFor="contact_email">Contact Email</Label>
                <Input id="contact_email" type="email" value={hotelForm.contact_email} onChange={(e) => setHotelForm({...hotelForm, contact_email: e.target.value})} />
              </div>
              <div>
                <Label htmlFor="contact_phone">Contact Phone</Label>
                <Input id="contact_phone" value={hotelForm.contact_phone} onChange={(e) => setHotelForm({...hotelForm, contact_phone: e.target.value})} />
              </div>
            </div>
            
            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label htmlFor="check_in_time">Check-in Time</Label>
                <Input id="check_in_time" type="time" value={hotelForm.check_in_time} onChange={(e) => setHotelForm({...hotelForm, check_in_time: e.target.value})} />
              </div>
              <div>
                <Label htmlFor="check_out_time">Check-out Time</Label>
                <Input id="check_out_time" type="time" value={hotelForm.check_out_time} onChange={(e) => setHotelForm({...hotelForm, check_out_time: e.target.value})} />
              </div>
            </div>
            
            <div>
              <Label htmlFor="hotel_images">Hotel Images</Label>
              <div className="space-y-2">
                <input
                  id="hotel_images"
                  type="file"
                  accept="image/*"
                  multiple
                  onChange={(e) => setHotelImageFiles(Array.from(e.target.files || []))}
                  className="hidden"
                />
                <Button
                  type="button"
                  variant="outline"
                  onClick={() => document.getElementById('hotel_images')?.click()}
                  disabled={uploadingHotelImages}
                >
                  {uploadingHotelImages ? 'Uploading...' : 'Choose Images'}
                </Button>
                {hotelImageFiles.length > 0 && (
                  <div className="text-sm text-gray-600">
                    {hotelImageFiles.length} image(s) selected
                  </div>
                )}
              </div>
            </div>
            
            <div>
              <Label htmlFor="description">Description</Label>
              <Textarea 
                id="description" 
                value={hotelForm.description} 
                onChange={(e) => setHotelForm({...hotelForm, description: e.target.value})} 
                placeholder="Describe your hotel property..."
                rows={3}
              />
            </div>
            
            <div>
              <Label htmlFor="amenities">Amenities (comma separated)</Label>
              <Textarea 
                id="amenities" 
                value={hotelForm.amenities} 
                onChange={(e) => setHotelForm({...hotelForm, amenities: e.target.value})} 
                placeholder="WiFi, Swimming Pool, Fitness Center, Restaurant, Spa, Business Center, Parking"
                rows={2}
              />
            </div>
            
            <div>
              <Label htmlFor="features">Room Features (comma separated)</Label>
              <Textarea 
                id="features" 
                value={hotelForm.features} 
                onChange={(e) => setHotelForm({...hotelForm, features: e.target.value})} 
                placeholder="Air Conditioning, Sea View, Balcony, Mini Bar, Room Service, Flat Screen TV"
                rows={2}
              />
            </div>
            
            <div>
              <Label htmlFor="cancellation_policy">Cancellation Policy</Label>
              <Textarea 
                id="cancellation_policy" 
                value={hotelForm.cancellation_policy} 
                onChange={(e) => setHotelForm({...hotelForm, cancellation_policy: e.target.value})} 
                placeholder="Free cancellation up to 24 hours before check-in..."
                rows={2}
              />
            </div>
            
            <div className="flex gap-2 pt-4">
              <Button onClick={handleSaveHotel}>{editingHotel ? 'Update Hotel' : 'Add Hotel'}</Button>
              <Button variant="outline" onClick={() => setIsModalOpen(false)}>Cancel</Button>
            </div>
          </div>
        </DialogContent>
      </Dialog>

      {/* Room Type Modal */}
      <Dialog open={isRoomModalOpen} onOpenChange={setIsRoomModalOpen}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle>{editingRoom ? 'Edit Room Type' : 'Add New Room Type'}</DialogTitle>
            <DialogDescription>
              {editingRoom ? 'Update the room type details below.' : 'Add a new room type to your hotel.'}
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label htmlFor="room_hotel">Hotel</Label>
                <Select value={roomForm.hotel_id} onValueChange={(value) => setRoomForm({...roomForm, hotel_id: value})}>
                  <SelectTrigger>
                    <SelectValue placeholder="Select hotel" />
                  </SelectTrigger>
                  <SelectContent>
                    {hotels.map((hotel) => (
                      <SelectItem key={hotel.id} value={hotel.id}>
                        {hotel.name}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              <div>
                <Label htmlFor="room_name">Room Name</Label>
                <Input id="room_name" value={roomForm.name} onChange={(e) => setRoomForm({...roomForm, name: e.target.value})} />
              </div>
            </div>
            
            <div className="grid grid-cols-3 gap-4">
              <div>
                <Label htmlFor="room_type">Room Type</Label>
                <Select value={roomForm.type} onValueChange={(value) => setRoomForm({...roomForm, type: value})}>
                  <SelectTrigger>
                    <SelectValue placeholder="Select type" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="standard">Standard</SelectItem>
                    <SelectItem value="deluxe">Deluxe</SelectItem>
                    <SelectItem value="suite">Suite</SelectItem>
                    <SelectItem value="presidential">Presidential</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div>
                <Label htmlFor="room_capacity">Capacity</Label>
                <Input id="room_capacity" type="number" value={roomForm.capacity} onChange={(e) => setRoomForm({...roomForm, capacity: Number(e.target.value)})} />
              </div>
              <div>
                <Label htmlFor="room_size">Size (m²)</Label>
                <Input id="room_size" type="number" value={roomForm.size_sqm} onChange={(e) => setRoomForm({...roomForm, size_sqm: Number(e.target.value)})} />
              </div>
            </div>
            
            <div className="grid grid-cols-3 gap-4">
              <div>
                <Label htmlFor="room_price">Price per Night</Label>
                <Input id="room_price" type="number" value={roomForm.price} onChange={(e) => setRoomForm({...roomForm, price: Number(e.target.value)})} />
              </div>
              <div>
                <Label htmlFor="room_count">Total Count</Label>
                <Input id="room_count" type="number" value={roomForm.total_count} onChange={(e) => setRoomForm({...roomForm, total_count: Number(e.target.value)})} />
              </div>
              <div>
                <Label htmlFor="bed_type">Bed Type</Label>
                <Select value={roomForm.bed_type} onValueChange={(value) => setRoomForm({...roomForm, bed_type: value})}>
                  <SelectTrigger>
                    <SelectValue placeholder="Select bed type" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="single">Single</SelectItem>
                    <SelectItem value="double">Double</SelectItem>
                    <SelectItem value="queen">Queen</SelectItem>
                    <SelectItem value="king">King</SelectItem>
                    <SelectItem value="twin">Twin</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>
            
            <div>
              <Label htmlFor="room_amenities">Room Amenities (comma separated)</Label>
              <Textarea 
                id="room_amenities" 
                value={roomForm.amenities} 
                onChange={(e) => setRoomForm({...roomForm, amenities: e.target.value})} 
                placeholder="Private Bathroom, Air Conditioning, Mini Bar, Safe, Balcony"
                rows={2}
              />
            </div>
            
            <div className="flex gap-2 pt-4">
              <Button onClick={handleSaveRoom}>{editingRoom ? 'Update Room Type' : 'Add Room Type'}</Button>
              <Button variant="outline" onClick={() => setIsRoomModalOpen(false)}>Cancel</Button>
            </div>
          </div>
        </DialogContent>
      </Dialog>

      <ConfirmDialog
        open={deleteConfirm.open}
        onOpenChange={(open) => setDeleteConfirm({ ...deleteConfirm, open })}
        title="Delete Hotel"
        description={`Are you sure you want to delete "${deleteConfirm.hotelName}"? This action cannot be undone.`}
        confirmText="Delete"
        variant="destructive"
        onConfirm={handleDeleteHotel}
      />
    </div>
  );
};