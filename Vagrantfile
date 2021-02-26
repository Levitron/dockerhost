Vagrant.configure("2") do |config|
    config.vm.provider "virtualbox" do |v|
  v.gui = true
  v.name = "dockerhost"
  v.memory = 4096
  v.cpus = 4
  end
  config.vm.box = "ubuntu/focal64"
  config.vm.provision "ansible" do |ansible|
      ansible.playbook = "ansible/dockerhost.yml"
    end
end
