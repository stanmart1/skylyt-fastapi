import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Users, Shield, Edit, Trash2, Plus } from 'lucide-react';
import { useAdmin } from '@/hooks/useAdmin';
import { useAuth } from '@/contexts/AuthContext';
import { User } from '@/types/api';

export const UserManagement = () => {
  const [users, setUsers] = useState<User[]>([]);
  const [roles, setRoles] = useState<any[]>([]);
  const [editingUser, setEditingUser] = useState<User | null>(null);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editForm, setEditForm] = useState({
    first_name: '',
    last_name: '',
    email: '',
    password: ''
  });
  const [addModalOpen, setAddModalOpen] = useState(false);
  const [addForm, setAddForm] = useState({
    first_name: '',
    last_name: '',
    email: '',
    password: '',
    role_id: ''
  });
  const [creating, setCreating] = useState(false);
  const { isLoading, getUsers, updateUserRole } = useAdmin();
  const { hasPermission } = useAuth();

  useEffect(() => {
    const fetchData = async () => {
      try {
        // Fetch users
        const userData = await getUsers();
        setUsers(Array.isArray(userData) ? userData : userData.users || []);
        
        // Fetch roles
        const { apiService } = await import('@/services/api');
        const rolesData = await apiService.request('/rbac/roles');
        setRoles(rolesData || []);
      } catch (error) {
        console.error('Failed to fetch data:', error);
      }
    };

    fetchData();
  }, [getUsers]);

  const handleRoleChange = async (userId: number, roleId: number) => {
    try {
      await updateUserRole(userId, roleId);
      // Refresh users list
      const userData = await getUsers();
      setUsers(Array.isArray(userData) ? userData : userData.users || []);
    } catch (error) {
      // Error handled in hook
    }
  };

  const handleEditUser = (user: User) => {
    setEditingUser(user);
    setEditForm({
      first_name: user.first_name,
      last_name: user.last_name,
      email: user.email,
      password: ''
    });
    setIsModalOpen(true);
  };

  const handleSaveUser = async () => {
    if (!editingUser) return;
    
    try {
      const { apiService } = await import('@/services/api');
      await apiService.updateUser(editingUser.id, editForm);
      
      // Refresh users list
      const userData = await getUsers();
      setUsers(Array.isArray(userData) ? userData : userData.users || []);
      
      setIsModalOpen(false);
      setEditingUser(null);
    } catch (error) {
      console.error('Failed to update user:', error);
    }
  };

  const handleDeleteUser = async (userId: number) => {
    try {
      const { apiService } = await import('@/services/api');
      await apiService.deleteUser(userId);
      
      // Refresh users list
      const userData = await getUsers();
      setUsers(Array.isArray(userData) ? userData : userData.users || []);
    } catch (error) {
      console.error('Failed to delete user:', error);
    }
  };

  const handleViewUserActivity = async (userId: number) => {
    try {
      const { apiService } = await import('@/services/api');
      const activityData = await apiService.request(`/admin/users/${userId}/activity`);
      // This would open a modal or navigate to user activity page
      console.log('User activity:', activityData);
    } catch (error) {
      console.error('Failed to fetch user activity:', error);
    }
  };

  const handleFlagSuspiciousActivity = async (userId: number) => {
    try {
      const { apiService } = await import('@/services/api');
      await apiService.request(`/admin/users/${userId}/flag-suspicious`, {
        method: 'POST'
      });
      
      // Refresh users list
      const userData = await getUsers();
      setUsers(Array.isArray(userData) ? userData : userData.users || []);
    } catch (error) {
      console.error('Failed to flag user:', error);
    }
  };

  const handleAddUser = async () => {
    if (!addForm.first_name || !addForm.last_name || !addForm.email || !addForm.password) {
      alert('Please fill in all required fields');
      return;
    }
    
    setCreating(true);
    try {
      const { apiService } = await import('@/services/api');
      await apiService.request('/rbac/users', {
        method: 'POST',
        body: JSON.stringify({
          first_name: addForm.first_name,
          last_name: addForm.last_name,
          email: addForm.email,
          password: addForm.password
        })
      });
      
      // Assign role if selected
      if (addForm.role_id) {
        const newUserData = await apiService.request('/rbac/users');
        const newUser = newUserData.users.find((u: any) => u.email === addForm.email);
        if (newUser) {
          await updateUserRole(newUser.id, Number(addForm.role_id));
        }
      }
      
      // Refresh users list
      const userData = await getUsers();
      setUsers(Array.isArray(userData) ? userData : userData.users || []);
      
      setAddModalOpen(false);
      setAddForm({ first_name: '', last_name: '', email: '', password: '', role_id: '' });
    } catch (error) {
      console.error('Failed to create user:', error);
      alert('Failed to create user');
    } finally {
      setCreating(false);
    }
  };

  const getRoleColor = (roleName: string) => {
    switch (roleName) {
      case 'superadmin': return 'bg-red-100 text-red-800';
      case 'admin': return 'bg-purple-100 text-purple-800';
      case 'accountant': return 'bg-blue-100 text-blue-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  if (isLoading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Users className="h-5 w-5" />
            User Management
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {[...Array(5)].map((_, i) => (
              <div key={i} className="animate-pulse">
                <div className="h-16 bg-gray-200 rounded" />
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <>
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle className="flex items-center gap-2">
            <Users className="h-5 w-5" />
            User Management
          </CardTitle>
          {hasPermission('users.create') && (
            <Button onClick={() => setAddModalOpen(true)}>
              <Plus className="h-4 w-4 mr-2" />
              Add User
            </Button>
          )}
        </div>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {users.map((user) => (
            <div key={user.id} className="flex items-center justify-between p-4 border rounded-lg">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 bg-blue-100 rounded-full flex items-center justify-center">
                  <Users className="h-5 w-5 text-blue-600" />
                </div>
                <div>
                  <h3 className="font-semibold">{user.full_name}</h3>
                  <p className="text-sm text-gray-600">{user.email}</p>
                  <div className="flex gap-1 mt-1">
                    {user.roles.map((role) => (
                      <Badge key={role.id} className={getRoleColor(role.name)}>
                        {role.name}
                      </Badge>
                    ))}
                  </div>
                </div>
              </div>
              <div className="flex items-center gap-2">
                {hasPermission('users.manage_roles') && (
                  <Select onValueChange={(value) => handleRoleChange(user.id, Number(value))}>
                    <SelectTrigger className="w-32">
                      <SelectValue placeholder="Change Role" />
                    </SelectTrigger>
                    <SelectContent>
                      {roles.map((role) => (
                        <SelectItem key={role.id} value={role.id.toString()}>
                          {role.name.charAt(0).toUpperCase() + role.name.slice(1)}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                )}
                {hasPermission('users.update') && (
                  <Button 
                    variant="outline" 
                    size="sm"
                    onClick={() => handleEditUser(user)}
                  >
                    <Edit className="h-3 w-3" />
                  </Button>
                )}
                {hasPermission('users.delete') && (
                  <Button 
                    variant="outline" 
                    size="sm"
                    onClick={() => handleDeleteUser(user.id)}
                    className="text-red-600 hover:text-red-700"
                  >
                    <Trash2 className="h-3 w-3" />
                  </Button>
                )}
              </div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>

    {/* Edit User Modal */}
    <Dialog open={isModalOpen} onOpenChange={setIsModalOpen}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Edit User</DialogTitle>
        </DialogHeader>
        <div className="space-y-4">
          <div>
            <Label htmlFor="first_name">First Name</Label>
            <Input
              id="first_name"
              value={editForm.first_name}
              onChange={(e) => setEditForm({...editForm, first_name: e.target.value})}
            />
          </div>
          <div>
            <Label htmlFor="last_name">Last Name</Label>
            <Input
              id="last_name"
              value={editForm.last_name}
              onChange={(e) => setEditForm({...editForm, last_name: e.target.value})}
            />
          </div>
          <div>
            <Label htmlFor="email">Email</Label>
            <Input
              id="email"
              type="email"
              value={editForm.email}
              onChange={(e) => setEditForm({...editForm, email: e.target.value})}
            />
          </div>
          <div>
            <Label htmlFor="password">New Password (optional)</Label>
            <Input
              id="password"
              type="password"
              value={editForm.password}
              onChange={(e) => setEditForm({...editForm, password: e.target.value})}
              placeholder="Leave blank to keep current password"
            />
          </div>
          <div className="flex gap-2 pt-4">
            <Button onClick={handleSaveUser}>Save Changes</Button>
            <Button variant="outline" onClick={() => setIsModalOpen(false)}>Cancel</Button>
          </div>
        </div>
      </DialogContent>
    </Dialog>

    {/* Add User Modal */}
    <Dialog open={addModalOpen} onOpenChange={setAddModalOpen}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Add New User</DialogTitle>
        </DialogHeader>
        <div className="space-y-4">
          <div>
            <Label htmlFor="add_first_name">First Name</Label>
            <Input
              id="add_first_name"
              value={addForm.first_name}
              onChange={(e) => setAddForm({...addForm, first_name: e.target.value})}
              required
            />
          </div>
          <div>
            <Label htmlFor="add_last_name">Last Name</Label>
            <Input
              id="add_last_name"
              value={addForm.last_name}
              onChange={(e) => setAddForm({...addForm, last_name: e.target.value})}
              required
            />
          </div>
          <div>
            <Label htmlFor="add_email">Email</Label>
            <Input
              id="add_email"
              type="email"
              value={addForm.email}
              onChange={(e) => setAddForm({...addForm, email: e.target.value})}
              required
            />
          </div>
          <div>
            <Label htmlFor="add_password">Password</Label>
            <Input
              id="add_password"
              type="password"
              value={addForm.password}
              onChange={(e) => setAddForm({...addForm, password: e.target.value})}
              required
            />
          </div>
          <div>
            <Label htmlFor="add_role">Role (Optional)</Label>
            <Select onValueChange={(value) => setAddForm({...addForm, role_id: value})}>
              <SelectTrigger>
                <SelectValue placeholder="Select a role" />
              </SelectTrigger>
              <SelectContent>
                {roles.map((role) => (
                  <SelectItem key={role.id} value={role.id.toString()}>
                    {role.name.charAt(0).toUpperCase() + role.name.slice(1)}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
          <div className="flex gap-2 pt-4">
            <Button onClick={handleAddUser} disabled={creating}>
              {creating ? 'Creating...' : 'Create User'}
            </Button>
            <Button variant="outline" onClick={() => setAddModalOpen(false)} disabled={creating}>
              Cancel
            </Button>
          </div>
        </div>
      </DialogContent>
    </Dialog>
    </>
  );
};